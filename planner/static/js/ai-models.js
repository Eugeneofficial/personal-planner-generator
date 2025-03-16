// AI Models Integration for Personal Planner Generator
// This file handles the integration with different AI models: ChatGPT, Grok, and Claude Sonnet

class AIModelManager {
    constructor() {
        this.currentModel = 'chatgpt'; // Default model
        this.modelOptions = {
            'chatgpt': {
                name: 'ChatGPT',
                icon: 'fa-comment-dots',
                description: 'OpenAI\'s ChatGPT - Versatile language model for general planner suggestions',
                color: '#10a37f' // OpenAI green
            },
            'grok': {
                name: 'Grok',
                icon: 'fa-robot',
                description: 'xAI\'s Grok - Creative and witty planner suggestions with personality',
                color: '#ff6b6b' // Vibrant red
            },
            'sonnet': {
                name: 'Claude Sonnet',
                icon: 'fa-feather-alt',
                description: 'Anthropic\'s Claude Sonnet - Thoughtful and nuanced planner suggestions',
                color: '#6c63ff' // Purple
            }
        };
    }

    // Initialize the AI model selector UI
    initModelSelector(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Create model selector UI
        let html = `
            <div class="ai-model-selector mb-4">
                <h6 class="mb-3">Choose AI Assistant:</h6>
                <div class="d-flex flex-wrap gap-2">
        `;

        // Add each model option
        for (const [modelId, model] of Object.entries(this.modelOptions)) {
            html += `
                <div class="ai-model-option ${modelId === this.currentModel ? 'active' : ''}" 
                     data-model="${modelId}" 
                     style="border-color: ${model.color}">
                    <i class="fas ${model.icon}" style="color: ${model.color}"></i>
                    <span>${model.name}</span>
                </div>
            `;
        }

        html += `
                </div>
                <div class="ai-model-description mt-2 small text-muted" id="modelDescription">
                    ${this.modelOptions[this.currentModel].description}
                </div>
            </div>
        `;

        container.innerHTML = html;

        // Add event listeners to model options
        const modelOptions = container.querySelectorAll('.ai-model-option');
        modelOptions.forEach(option => {
            option.addEventListener('click', () => {
                // Update active state
                modelOptions.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');

                // Update current model
                this.currentModel = option.getAttribute('data-model');
                
                // Update description
                const descriptionEl = document.getElementById('modelDescription');
                if (descriptionEl) {
                    descriptionEl.textContent = this.modelOptions[this.currentModel].description;
                }
            });
        });
    }

    // Get suggestions from the selected AI model
    async getSuggestions(prompt) {
        // Show different behavior based on selected model
        console.log(`Getting suggestions from ${this.modelOptions[this.currentModel].name}`);
        
        // In a real implementation, this would call different API endpoints
        // For now, we'll simulate different responses based on the model
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Generate model-specific suggestions
        switch(this.currentModel) {
            case 'chatgpt':
                return this.getChatGPTSuggestions(prompt);
            case 'grok':
                return this.getGrokSuggestions(prompt);
            case 'sonnet':
                return this.getSonnetSuggestions(prompt);
            default:
                return this.getChatGPTSuggestions(prompt);
        }
    }
    
    // ChatGPT suggestions - balanced and helpful
    getChatGPTSuggestions(prompt) {
        const suggestions = [];
        
        // Base suggestions on prompt keywords
        if (prompt.toLowerCase().includes('student') || prompt.toLowerCase().includes('study')) {
            suggestions.push({
                title: 'Study Schedule Optimizer',
                description: 'AI-generated optimal study schedule based on your course load and learning preferences.'
            });
            suggestions.push({
                title: 'Assignment Priority System',
                description: 'Smart prioritization system for assignments with deadline reminders and difficulty ratings.'
            });
        }
        
        if (prompt.toLowerCase().includes('work') || prompt.toLowerCase().includes('professional')) {
            suggestions.push({
                title: 'Meeting Preparation Framework',
                description: 'Pre-meeting preparation checklist with talking points and follow-up task automation.'
            });
            suggestions.push({
                title: 'Work-Life Balance Monitor',
                description: 'Track work hours and receive suggestions for maintaining healthy boundaries.'
            });
        }
        
        if (prompt.toLowerCase().includes('health') || prompt.toLowerCase().includes('fitness')) {
            suggestions.push({
                title: 'Wellness Integration',
                description: 'Combine your fitness goals with your daily schedule for balanced health planning.'
            });
            suggestions.push({
                title: 'Nutrition and Hydration Tracker',
                description: 'Smart tracking of meals and water intake with personalized recommendations.'
            });
        }
        
        // Add general suggestions if needed
        if (suggestions.length < 3) {
            suggestions.push({
                title: 'Smart Task Prioritization',
                description: 'AI-powered system to organize your tasks by urgency, importance, and estimated time.'
            });
            suggestions.push({
                title: 'Focus Time Blocks',
                description: 'Dedicated distraction-free time blocks with productivity metrics and insights.'
            });
            suggestions.push({
                title: 'Reflection Prompts',
                description: 'Daily guided reflection questions to improve self-awareness and growth.'
            });
        }
        
        return suggestions;
    }
    
    // Grok suggestions - more creative and witty
    getGrokSuggestions(prompt) {
        const suggestions = [];
        
        // Base suggestions on prompt keywords with Grok's personality
        if (prompt.toLowerCase().includes('student') || prompt.toLowerCase().includes('study')) {
            suggestions.push({
                title: 'Procrastination Destroyer 3000',
                description: 'Turn studying from "I\'ll do it tomorrow" to "I finished it yesterday" with this clever system.'
            });
            suggestions.push({
                title: 'The "Actually Readable" Notes Section',
                description: 'Because let\'s face it, you can\'t read your own handwriting. AI-organized notes that make sense later.'
            });
        }
        
        if (prompt.toLowerCase().includes('work') || prompt.toLowerCase().includes('professional')) {
            suggestions.push({
                title: 'Meeting Survival Kit',
                description: 'For when that "quick sync" turns into a 2-hour discussion about the office coffee machine.'
            });
            suggestions.push({
                title: 'The "No, I Can\'t Work Weekends" Reminder',
                description: 'Automatic boundaries for workaholics. Includes excuses generator for last-minute requests!'
            });
        }
        
        if (prompt.toLowerCase().includes('health') || prompt.toLowerCase().includes('fitness')) {
            suggestions.push({
                title: 'The Realistic Workout Plan',
                description: 'No more "I\'ll run 10 miles daily" delusions. Start with "take the stairs" and work up from there.'
            });
            suggestions.push({
                title: 'Snack Attack Defender',
                description: 'Track your nutrition with a system that doesn\'t judge you for that midnight ice cream.'
            });
        }
        
        // Add general suggestions if needed
        if (suggestions.length < 3) {
            suggestions.push({
                title: 'The "Where Did My Day Go?" Tracker',
                description: 'Find out you spent 4 hours on social media when you thought it was 10 minutes. Knowledge is power!'
            });
            suggestions.push({
                title: 'Excuse Generator Pro',
                description: 'For when "my dog ate my homework" doesn\'t cut it anymore. Fresh, believable excuses daily.'
            });
            suggestions.push({
                title: 'Motivation Kickstarter',
                description: 'When "you can do it" isn\'t cutting it, try "remember that embarrassing thing you did 10 years ago?"'
            });
        }
        
        return suggestions;
    }
    
    // Claude Sonnet suggestions - thoughtful and nuanced
    getSonnetSuggestions(prompt) {
        const suggestions = [];
        
        // Base suggestions on prompt keywords with Claude's thoughtful approach
        if (prompt.toLowerCase().includes('student') || prompt.toLowerCase().includes('study')) {
            suggestions.push({
                title: 'Holistic Learning Framework',
                description: 'Integrate knowledge across subjects with connections that deepen understanding and retention.'
            });
            suggestions.push({
                title: 'Cognitive Energy Management',
                description: 'Schedule study sessions based on your natural energy patterns for optimal learning efficiency.'
            });
        }
        
        if (prompt.toLowerCase().includes('work') || prompt.toLowerCase().includes('professional')) {
            suggestions.push({
                title: 'Meaningful Contribution Tracker',
                description: 'Focus on impact rather than hours, with reflection on how your work aligns with your values.'
            });
            suggestions.push({
                title: 'Collaborative Harmony System',
                description: 'Balance individual focus with team collaboration through thoughtfully structured communication.'
            });
        }
        
        if (prompt.toLowerCase().includes('health') || prompt.toLowerCase().includes('fitness')) {
            suggestions.push({
                title: 'Mindful Movement Integration',
                description: 'Connect physical activity with mental wellbeing through intentional exercise and reflection.'
            });
            suggestions.push({
                title: 'Nourishment Philosophy',
                description: 'Develop a thoughtful relationship with food beyond calories—focus on energy, enjoyment, and ethics.'
            });
        }
        
        // Add general suggestions if needed
        if (suggestions.length < 3) {
            suggestions.push({
                title: 'Value-Aligned Daily Practices',
                description: 'Ensure your daily activities reflect your deeper values and long-term aspirations.'
            });
            suggestions.push({
                title: 'Contemplative Time Blocks',
                description: 'Schedule regular periods for deep thinking and reflection to enhance creativity and clarity.'
            });
            suggestions.push({
                title: 'Relationship Nurturing System',
                description: 'Intentionally maintain meaningful connections with thoughtful reminders and interaction planning.'
            });
        }
        
        return suggestions;
    }
}

// Initialize and export the AI model manager
const aiModelManager = new AIModelManager(); 