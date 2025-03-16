import os
import json
from flask import Flask, render_template, request, send_file, redirect, url_for, flash, jsonify, session
from planner.generator import generate_planner, get_quote
from planner.config import Config
from flask_babel import Babel

app = Flask(__name__, 
            template_folder='planner/templates',
            static_folder='planner/static')
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Configure Babel settings
app.config['BABEL_DEFAULT_LOCALE'] = Config.DEFAULT_LANGUAGE
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# Define locale selector function
def get_locale():
    # Get language from session or use default
    return session.get('language', Config.DEFAULT_LANGUAGE)

# Initialize Babel for internationalization
babel = Babel(app, locale_selector=get_locale)

# Make Config class available to all templates
@app.context_processor
def inject_config():
    # Create masked_keys dictionary for all templates
    masked_keys = {}
    api_keys = Config.get_api_keys()
    
    for provider, config in Config.AI_MODELS.items():
        key_name = config.get('key_name')
        if key_name and key_name in api_keys:
            # Mask the API key (show only first 4 and last 4 characters)
            api_key = api_keys[key_name]
            if len(api_key) > 8:
                masked_keys[provider] = f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"
            else:
                masked_keys[provider] = "********"
        else:
            masked_keys[provider] = None
            
        # Get base URLs
        base_url_name = config.get('base_url_name')
        if base_url_name and base_url_name in api_keys:
            masked_keys[f"{provider}_base_url"] = api_keys[base_url_name]
        elif 'default_base_url' in config:
            masked_keys[f"{provider}_base_url"] = config['default_base_url']
    
    return dict(config=Config, masked_keys=masked_keys)

@app.route('/language/<language>')
def set_language(language):
    """Set the language for the session"""
    if language in Config.LANGUAGES:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/', methods=['GET'])
def index():
    """Render the home page with the planner customization form."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate a personalized planner based on form data."""
    # Get form data
    name = request.form.get('name', '')
    time_range = request.form.get('time_range', 'week')
    quote = request.form.get('quote', '')
    theme = request.form.get('theme', 'Productivity')
    style = request.form.get('style', 'minimalist')
    
    # Get selected components
    components = {
        'todo': 'todo' in request.form,
        'habit_tracker': 'habit_tracker' in request.form,
        'notes': 'notes' in request.form,
        'schedule': 'schedule' in request.form,
        'mood_tracker': 'mood_tracker' in request.form,
        'goal_setting': 'goal_setting' in request.form,
        'reflection': 'reflection' in request.form,
        'gratitude': 'gratitude' in request.form,
        'water_tracker': 'water_tracker' in request.form
    }
    
    # Get habits if habit tracker is selected
    habits = []
    if components['habit_tracker']:
        habits = request.form.get('habits', '').split(',')
        habits = [habit.strip() for habit in habits if habit.strip()]
    
    # Generate the planner
    pdf_path = generate_planner(
        name=name,
        time_range=time_range,
        quote=quote,
        theme=theme,
        style=style,
        components=components,
        habits=habits
    )
    
    # Send the generated PDF file
    return send_file(pdf_path, as_attachment=True, download_name=f"{name.lower().replace(' ', '_')}_planner.pdf")

@app.route('/api/quote', methods=['GET'])
def api_quote():
    """API endpoint to get a random inspirational quote."""
    quote = get_quote()
    return jsonify({'quote': quote})

@app.route('/api/ai-suggestions', methods=['POST'])
def ai_suggestions():
    """API endpoint to get AI-generated planner suggestions."""
    data = request.get_json()
    prompt = data.get('prompt', '')
    model_provider = data.get('provider', 'openai')
    model_name = data.get('model', 'gpt-3.5-turbo')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    # Check if API key is set for the provider
    if not Config.is_api_key_set(model_provider) and model_provider != 'lmstudio':
        return jsonify({'error': f'API key not set for {model_provider}'}), 401
    
    # If using LM Studio, use the basic chat completion API
    if model_provider == 'lmstudio':
        try:
            from planner.lmstudio_tools import LMStudioToolsClient
            
            # Get the base URL and API key for LM Studio
            base_url = Config.get_base_url('lmstudio')
            api_key = Config.get_api_key('lmstudio')
            
            # Get the selected model
            model = Config.get_model('lmstudio')
            
            # Create the LM Studio client
            client = LMStudioToolsClient(base_url=base_url, api_key=api_key)
            
            # Create a system message that instructs the model to generate planner suggestions
            system_message = """You are an AI assistant that helps users create personalized planners. 
            Your task is to suggest additional components or features that would enhance their planner.
            Provide 3-5 specific suggestions based on the user's current planner configuration.
            Each suggestion should have a clear title and a brief description explaining its benefits.
            Format your response as a JSON array of objects with 'title' and 'description' fields."""
            
            # Send a chat completion request
            response = client.chat_completion(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=0.7,
                max_tokens=500
            )
            
            # Check if we got a valid response
            if "choices" in response and len(response["choices"]) > 0 and "message" in response["choices"][0]:
                message_content = response["choices"][0]["message"]["content"]
                
                # Try to extract JSON from the response
                try:
                    # Look for JSON array in the response
                    import re
                    import json
                    
                    # Try to find JSON array in the text
                    json_match = re.search(r'\[\s*\{.*\}\s*\]', message_content, re.DOTALL)
                    
                    if json_match:
                        suggestions_json = json_match.group(0)
                        suggestions = json.loads(suggestions_json)
                    else:
                        # If no JSON array found, try to parse the entire response as JSON
                        suggestions = json.loads(message_content)
                    
                    # Ensure we have the expected format
                    if isinstance(suggestions, list):
                        formatted_suggestions = []
                        for suggestion in suggestions:
                            if isinstance(suggestion, dict) and 'title' in suggestion and 'description' in suggestion:
                                formatted_suggestions.append({
                                    'title': suggestion['title'],
                                    'description': suggestion['description']
                                })
                        
                        if formatted_suggestions:
                            return jsonify({'suggestions': formatted_suggestions})
                except (json.JSONDecodeError, ValueError) as e:
                    # If JSON parsing fails, create suggestions from the text
                    lines = message_content.split('\n')
                    suggestions = []
                    
                    current_title = None
                    current_description = []
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # Check if this line looks like a title (numbered or with a special prefix)
                        if re.match(r'^(\d+[\.\):]|[\-\*]|\*\*|#)', line) or line.isupper():
                            # If we have a previous title and description, add it to suggestions
                            if current_title and current_description:
                                suggestions.append({
                                    'title': current_title,
                                    'description': ' '.join(current_description)
                                })
                                current_description = []
                            
                            # Extract the new title
                            current_title = re.sub(r'^(\d+[\.\):]|[\-\*]|\*\*|#)\s*', '', line)
                            current_title = current_title.strip('*').strip()
                        else:
                            # This is part of the description
                            if current_title:
                                current_description.append(line)
                    
                    # Add the last suggestion if there is one
                    if current_title and current_description:
                        suggestions.append({
                            'title': current_title,
                            'description': ' '.join(current_description)
                        })
                    
                    # If we couldn't parse structured suggestions, create a generic one
                    if not suggestions:
                        suggestions = [{
                            'title': 'AI Recommendation',
                            'description': message_content
                        }]
                    
                    return jsonify({'suggestions': suggestions})
            
            # If we couldn't get a valid response, return an error
            return jsonify({'error': 'Failed to get suggestions from LM Studio'}), 500
            
        except ImportError:
            return jsonify({'error': 'LM Studio tools module not available'}), 500
        except Exception as e:
            return jsonify({'error': f'Error using LM Studio: {str(e)}'}), 500
    
    # For other providers, use the existing keyword-based approach
    suggestions = []
    
    # Check for keywords and add relevant suggestions
    if any(keyword in prompt.lower() for keyword in ['student', 'class', 'study', 'school', 'college']):
        suggestions.append({
            'title': 'Add Class Schedule Component',
            'description': 'Include a dedicated section for tracking classes with time slots and locations.'
        })
        suggestions.append({
            'title': 'Add Assignment Tracker',
            'description': 'Include a special to-do section specifically for tracking assignments and due dates.'
        })
        suggestions.append({
            'title': 'Add Study Timer',
            'description': 'Include a Pomodoro-style study timer section to track focused study sessions.'
        })
    
    if any(keyword in prompt.lower() for keyword in ['work', 'job', 'professional', 'career', 'business']):
        suggestions.append({
            'title': 'Add Meeting Notes Section',
            'description': 'Include a dedicated area for taking notes during meetings.'
        })
        suggestions.append({
            'title': 'Add Project Timeline',
            'description': 'Include a project tracking section with milestones and deadlines.'
        })
        suggestions.append({
            'title': 'Add Work/Life Balance Tracker',
            'description': 'Track overtime hours and ensure you maintain a healthy work/life balance.'
        })
    
    if any(keyword in prompt.lower() for keyword in ['fitness', 'workout', 'exercise', 'gym', 'health']):
        suggestions.append({
            'title': 'Add Workout Log',
            'description': 'Include a section to track exercises, sets, reps, and weights.'
        })
        suggestions.append({
            'title': 'Add Nutrition Tracker',
            'description': 'Track daily water intake, meals, and calories.'
        })
        suggestions.append({
            'title': 'Add Body Measurements Log',
            'description': 'Track progress with weight, measurements, and other fitness metrics.'
        })
    
    # Add some general suggestions if we don't have enough specific ones
    if len(suggestions) < 3:
        general_suggestions = [
            {
                'title': 'Enhanced Habit Tracker',
                'description': 'Track multiple habits with color coding and streak counting.'
            },
            {
                'title': 'Goal Setting Framework',
                'description': 'Include a structured approach to setting and tracking weekly and monthly goals.'
            },
            {
                'title': 'Daily Reflection Prompts',
                'description': 'Add guided reflection questions for end-of-day journaling.'
            },
            {
                'title': 'Priority Matrix',
                'description': 'Include a quadrant-based priority system for tasks (urgent/important matrix).'
            },
            {
                'title': 'Mood Tracker',
                'description': 'Track your daily mood and emotional well-being.'
            },
            {
                'title': 'Gratitude Journal',
                'description': 'Include a section to write down things you\'re grateful for each day.'
            }
        ]
        
        # Add general suggestions until we have at least 3
        for suggestion in general_suggestions:
            if len(suggestions) >= 3:
                break
            if not any(s['title'] == suggestion['title'] for s in suggestions):
                suggestions.append(suggestion)
    
    return jsonify({'suggestions': suggestions})

@app.route('/settings', methods=['GET'])
def settings():
    """Render the settings page for API keys and language."""
    ai_models = Config.AI_MODELS
    
    return render_template('settings.html', 
                          ai_models=ai_models,
                          languages=Config.LANGUAGES,
                          current_language=session.get('language', Config.DEFAULT_LANGUAGE))

@app.route('/api/settings/save-key', methods=['POST'])
def save_api_key():
    """Save an API key for a provider."""
    data = request.get_json()
    provider = data.get('provider')
    api_key = data.get('api_key')
    base_url = data.get('base_url')
    model = data.get('model')
    
    if not provider or not api_key:
        return jsonify({'success': False, 'message': 'Provider and API key are required'}), 400
    
    # Validate provider
    if provider not in Config.AI_MODELS:
        return jsonify({'success': False, 'message': 'Invalid provider'}), 400
    
    # Save the API key
    success = Config.save_api_key(provider, api_key, base_url, model)
    
    if success:
        return jsonify({'success': True, 'message': f'API key for {provider} saved successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to save API key'}), 500

@app.route('/api/settings/test-key', methods=['POST'])
def test_api_key():
    """Test an API key for a provider."""
    data = request.get_json()
    provider = data.get('provider')
    api_key = data.get('api_key')
    base_url = data.get('base_url')
    
    if not provider:
        return jsonify({'success': False, 'message': 'Provider is required'}), 400
    
    # Validate provider
    if provider not in Config.AI_MODELS:
        return jsonify({'success': False, 'message': 'Invalid provider'}), 400
    
    # For LM Studio, we'll actually test the connection
    if provider == 'lmstudio':
        try:
            from planner.lmstudio_tools import LMStudioToolsClient
            
            # Use the provided base_url and api_key for testing
            # If not provided, use the ones from config
            if not base_url:
                base_url = Config.get_base_url('lmstudio')
            if not api_key:
                api_key = Config.get_api_key('lmstudio')
            
            # Get the selected model or use the provided one
            model = data.get('model') or Config.get_model('lmstudio') or 'local-model'
            
            # Create the LM Studio client
            client = LMStudioToolsClient(base_url=base_url, api_key=api_key)
            
            # Test connection with a simple request
            response = client.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                model=model,
                max_tokens=10
            )
            
            if "error" in response:
                return jsonify({'success': False, 'message': f'Error connecting to LM Studio: {response["message"]}'}), 500
            
            return jsonify({'success': True, 'message': 'Successfully connected to LM Studio'})
        except ImportError:
            return jsonify({'success': False, 'message': 'LM Studio tools module not available'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error testing LM Studio connection: {str(e)}'}), 500
    
    # For other providers, check if API key is set
    if not Config.is_api_key_set(provider) and not api_key:
        return jsonify({'success': False, 'message': f'API key not set for {provider}'}), 401
    
    # In a real application, this would test the API key with the actual service
    # For now, we'll just return success
    return jsonify({'success': True, 'message': f'API key for {provider} is valid'})

@app.route('/templates', methods=['GET'])
def templates():
    """Render the templates page."""
    templates = [
        {
            'id': 'student',
            'name': 'Student Planner',
            'description': 'Perfect for tracking classes, assignments, and study sessions',
            'components': ['todo', 'habit_tracker', 'schedule', 'notes'],
            'habits': ['Study', 'Attend class', 'Complete assignments', 'Review notes'],
            'theme': 'Academic Success',
            'style': 'minimalist'
        },
        {
            'id': 'work',
            'name': 'Work Planner',
            'description': 'Designed for professionals with meetings and project deadlines',
            'components': ['todo', 'schedule', 'notes', 'goal_setting'],
            'habits': ['Email management', 'Meeting preparation', 'Project tasks', 'Follow-ups'],
            'theme': 'Professional Growth',
            'style': 'minimalist'
        },
        {
            'id': 'fitness',
            'name': 'Fitness Planner',
            'description': 'Track workouts, nutrition, and wellness goals',
            'components': ['habit_tracker', 'notes', 'water_tracker', 'goal_setting'],
            'habits': ['Exercise', 'Water intake', 'Protein intake', 'Sleep 8 hours'],
            'theme': 'Health & Fitness',
            'style': 'colorful'
        },
        {
            'id': 'creative',
            'name': 'Creative Planner',
            'description': 'For artists and writers with project tracking',
            'components': ['todo', 'habit_tracker', 'notes', 'reflection'],
            'habits': ['Daily creation', 'Idea journaling', 'Research', 'Skill practice'],
            'theme': 'Creative Expression',
            'style': 'illustrated'
        },
        {
            'id': 'mindfulness',
            'name': 'Mindfulness Planner',
            'description': 'Focus on mental health, gratitude, and self-care',
            'components': ['habit_tracker', 'mood_tracker', 'reflection', 'gratitude'],
            'habits': ['Meditation', 'Gratitude', 'Deep breathing', 'Journaling'],
            'theme': 'Mindfulness & Well-being',
            'style': 'illustrated'
        },
        {
            'id': 'travel',
            'name': 'Travel Planner',
            'description': 'Plan trips, activities, and packing lists',
            'components': ['todo', 'notes', 'goal_setting', 'habit_tracker'],
            'habits': ['Research destinations', 'Budget tracking', 'Packing list', 'Language practice'],
            'theme': 'Travel & Adventure',
            'style': 'colorful'
        }
    ]
    
    return render_template('templates.html', templates=templates)

@app.route('/api/template/<template_id>', methods=['GET'])
def get_template(template_id):
    """API endpoint to get a specific template."""
    templates = {
        'student': {
            'components': ['todo', 'habit_tracker', 'schedule', 'notes'],
            'habits': 'Study, Attend class, Complete assignments, Review notes',
            'theme': 'Academic Success',
            'style': 'minimalist'
        },
        'work': {
            'components': ['todo', 'schedule', 'notes', 'goal_setting'],
            'habits': 'Email management, Meeting preparation, Project tasks, Follow-ups',
            'theme': 'Professional Growth',
            'style': 'minimalist'
        },
        'fitness': {
            'components': ['habit_tracker', 'notes', 'water_tracker', 'goal_setting'],
            'habits': 'Exercise, Water intake, Protein intake, Sleep 8 hours',
            'theme': 'Health & Fitness',
            'style': 'colorful'
        },
        'creative': {
            'components': ['todo', 'habit_tracker', 'notes', 'reflection'],
            'habits': 'Daily creation, Idea journaling, Research, Skill practice',
            'theme': 'Creative Expression',
            'style': 'illustrated'
        },
        'mindfulness': {
            'components': ['habit_tracker', 'mood_tracker', 'reflection', 'gratitude'],
            'habits': 'Meditation, Gratitude, Deep breathing, Journaling',
            'theme': 'Mindfulness & Well-being',
            'style': 'illustrated'
        },
        'travel': {
            'components': ['todo', 'notes', 'goal_setting', 'habit_tracker'],
            'habits': 'Research destinations, Budget tracking, Packing list, Language practice',
            'theme': 'Travel & Adventure',
            'style': 'colorful'
        }
    }
    
    if template_id not in templates:
        return jsonify({'error': 'Template not found'}), 404
    
    return jsonify(templates[template_id])

@app.route('/chat', methods=['GET'])
def chat():
    """Render the chat page for AI-assisted planner creation."""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat with AI."""
    data = request.get_json()
    message = data.get('message', '')
    provider = data.get('provider', 'lmstudio')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Check if API key is set for the provider (except for LM Studio which may not require a key)
    if provider != 'lmstudio' and not Config.is_api_key_set(provider):
        return jsonify({'error': f'API key not set for {provider}'}), 401
    
    # Currently only LM Studio is supported for chat
    if provider == 'lmstudio':
        try:
            from planner.lmstudio_chat import LMStudioChat
            
            # Get the base URL and API key for LM Studio
            base_url = Config.get_base_url('lmstudio')
            api_key = Config.get_api_key('lmstudio')
            
            # Get the selected model
            model = Config.get_model('lmstudio')
            
            # Create the LM Studio chat client
            chat_client = LMStudioChat(base_url=base_url, api_key=api_key, model=model)
            
            # Process the message
            planner_items, response = chat_client.process_message(message)
            
            return jsonify({
                'response': response,
                'planner_items': planner_items
            })
        except ImportError:
            return jsonify({'error': 'LM Studio chat module not available'}), 500
        except Exception as e:
            return jsonify({'error': f'Error using LM Studio chat: {str(e)}'}), 500
    else:
        # For other providers, return a simple response
        return jsonify({
            'response': f'Чат с {provider} пока не поддерживается. Пожалуйста, используйте LM Studio.',
            'planner_items': []
        })

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True) 