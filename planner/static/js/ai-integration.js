/**
 * AI Integration Module
 * Handles interactions with various AI models for the Personal Planner Generator
 */

class AIModelManager {
    constructor() {
        this.apiEndpoint = '/api/ai/generate';
        this.testEndpoint = '/api/settings/test-key';
        this.providers = {
            openai: {
                name: 'ChatGPT',
                icon: 'fa-comment-dots',
                color: '#10a37f',
                requiresKey: true,
                baseUrlConfigurable: true,
                defaultPrompt: 'Suggest planner components that would help with productivity and work-life balance.'
            },
            anthropic: {
                name: 'Claude',
                icon: 'fa-feather-alt',
                color: '#6c63ff',
                requiresKey: true,
                baseUrlConfigurable: true,
                defaultPrompt: 'What planner elements would be most helpful for someone trying to organize their life?'
            },
            google: {
                name: 'Gemini',
                icon: 'fa-brain',
                color: '#4285F4',
                requiresKey: true,
                baseUrlConfigurable: true,
                defaultPrompt: 'Recommend planner features for someone who wants to improve their time management.'
            },
            lmstudio: {
                name: 'LM Studio',
                icon: 'fa-robot',
                color: '#ff6b6b',
                requiresKey: false,
                baseUrlConfigurable: true,
                defaultPrompt: 'What are some creative planner components I could add to make my planner more fun and useful?'
            }
        };
        
        // Initialize with default provider
        this.currentProvider = localStorage.getItem('currentAiProvider') || 'openai';
    }
    
    /**
     * Generate AI suggestions based on planner configuration
     * @param {Object} plannerConfig - The current planner configuration
     * @param {Function} callback - Callback function to handle the response
     */
    generateSuggestion(plannerConfig, callback) {
        const provider = this.currentProvider;
        const language = document.documentElement.lang || 'en';
        
        // Create request payload
        const payload = {
            provider: provider,
            language: language,
            config: plannerConfig,
            prompt: this.providers[provider].defaultPrompt
        };
        
        // Show loading state
        callback({
            loading: true,
            provider: provider,
            providerInfo: this.providers[provider]
        });
        
        // Make API request
        fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            callback({
                loading: false,
                success: true,
                provider: provider,
                providerInfo: this.providers[provider],
                suggestion: data.suggestion,
                components: data.components || []
            });
        })
        .catch(error => {
            console.error('Error generating AI suggestion:', error);
            callback({
                loading: false,
                success: false,
                provider: provider,
                providerInfo: this.providers[provider],
                error: error.message
            });
        });
    }
    
    /**
     * Test if an API key is valid for a provider
     * @param {String} provider - The AI provider to test
     * @param {String} apiKey - The API key to test
     * @param {String} baseUrl - Optional base URL for the API
     * @param {Function} callback - Callback function to handle the response
     */
    testApiKey(provider, apiKey, baseUrl, callback) {
        if (!this.providers[provider]) {
            callback({
                success: false,
                error: 'Invalid provider'
            });
            return;
        }
        
        // Create request payload
        const payload = {
            provider: provider,
            api_key: apiKey
        };
        
        if (baseUrl) {
            payload.base_url = baseUrl;
        }
        
        // Make API request
        fetch(this.testEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            callback({
                success: true,
                message: data.message
            });
        })
        .catch(error => {
            console.error('Error testing API key:', error);
            callback({
                success: false,
                error: error.message
            });
        });
    }
    
    /**
     * Get available AI models
     * @returns {Object} Object containing available AI models
     */
    getAvailableModels() {
        return this.providers;
    }
    
    /**
     * Set the current AI provider
     * @param {String} provider - The provider to set as current
     */
    setCurrentProvider(provider) {
        if (this.providers[provider]) {
            this.currentProvider = provider;
            localStorage.setItem('currentAiProvider', provider);
            return true;
        }
        return false;
    }
    
    /**
     * Get the current AI provider
     * @returns {String} The current provider ID
     */
    getCurrentProvider() {
        return this.currentProvider;
    }
    
    /**
     * Get information about the current provider
     * @returns {Object} Provider information
     */
    getCurrentProviderInfo() {
        return this.providers[this.currentProvider];
    }
}

// Initialize the AI Model Manager
const aiModelManager = new AIModelManager();

// Export for use in other modules
window.aiModelManager = aiModelManager;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AI suggestions on the planner page
    const aiSuggestionsLink = document.getElementById('aiSuggestionsLink');
    if (aiSuggestionsLink) {
        aiSuggestionsLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the AI suggestions button on the main page and click it
            const getAiSuggestionsBtn = document.getElementById('getAiSuggestionsBtn');
            if (getAiSuggestionsBtn) {
                getAiSuggestionsBtn.click();
                // Scroll to the AI suggestions section
                document.getElementById('aiSuggestions').scrollIntoView({ behavior: 'smooth' });
            } else {
                // If not on the main page, redirect to it
                window.location.href = '/';
            }
        });
    }
    
    // Handle AI model selection
    const aiModelItems = document.querySelectorAll('.ai-model-item');
    aiModelItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const provider = this.getAttribute('data-provider');
            if (provider) {
                aiModelManager.setCurrentProvider(provider);
            }
        });
    });
    
    // Add font size controls for better readability
    addFontSizeControls();
    
    // Add high contrast mode toggle
    addHighContrastModeToggle();
    
    // Templates link
    const templatesLink = document.getElementById('templatesLink');
    if (templatesLink) {
        templatesLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Create modal if it doesn't exist
            let templatesModal = document.getElementById('templatesModal');
            if (!templatesModal) {
                templatesModal = document.createElement('div');
                templatesModal.className = 'modal fade';
                templatesModal.id = 'templatesModal';
                templatesModal.setAttribute('tabindex', '-1');
                templatesModal.innerHTML = `
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title"><i class="fas fa-th-large me-2"></i>Planner Templates</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-4 mb-4">
                                        <div class="card template-card">
                                            <div class="card-body text-center">
                                                <h5>Student Planner</h5>
                                                <p class="small">Perfect for tracking classes, assignments, and study sessions</p>
                                                <button class="btn btn-sm btn-primary use-template" data-template="student">Use Template</button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 mb-4">
                                        <div class="card template-card">
                                            <div class="card-body text-center">
                                                <h5>Work Planner</h5>
                                                <p class="small">Designed for professionals with meetings and project deadlines</p>
                                                <button class="btn btn-sm btn-primary use-template" data-template="work">Use Template</button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 mb-4">
                                        <div class="card template-card">
                                            <div class="card-body text-center">
                                                <h5>Fitness Planner</h5>
                                                <p class="small">Track workouts, nutrition, and wellness goals</p>
                                                <button class="btn btn-sm btn-primary use-template" data-template="fitness">Use Template</button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 mb-4">
                                        <div class="card template-card">
                                            <div class="card-body text-center">
                                                <h5>Creative Planner</h5>
                                                <p class="small">For artists and writers with project tracking</p>
                                                <button class="btn btn-sm btn-primary use-template" data-template="creative">Use Template</button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 mb-4">
                                        <div class="card template-card">
                                            <div class="card-body text-center">
                                                <h5>Mindfulness Planner</h5>
                                                <p class="small">Focus on mental health, gratitude, and self-care</p>
                                                <button class="btn btn-sm btn-primary use-template" data-template="mindfulness">Use Template</button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 mb-4">
                                        <div class="card template-card">
                                            <div class="card-body text-center">
                                                <h5>Travel Planner</h5>
                                                <p class="small">Plan trips, activities, and packing lists</p>
                                                <button class="btn btn-sm btn-primary use-template" data-template="travel">Use Template</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                `;
                document.body.appendChild(templatesModal);
                
                // Initialize the modal
                const bsModal = new bootstrap.Modal(templatesModal);
                
                // Add event listeners to template buttons
                document.querySelectorAll('.use-template').forEach(button => {
                    button.addEventListener('click', function() {
                        const templateType = this.getAttribute('data-template');
                        applyTemplate(templateType);
                        bsModal.hide();
                    });
                });
                
                // Show the modal
                bsModal.show();
            } else {
                // If modal already exists, just show it
                const bsModal = new bootstrap.Modal(templatesModal);
                bsModal.show();
            }
        });
    }
});

// Function to apply selected suggestions
function applySuggestions(selectedIndices) {
    // This would normally update the form based on the selected suggestions
    // For now, we'll just simulate it by showing a toast notification
    
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '11';
    toast.innerHTML = `
        <div id="suggestionToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto"><i class="fas fa-magic me-2"></i>AI Suggestions Applied</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${selectedIndices.length} suggestion(s) have been applied to your planner.
            </div>
        </div>
    `;
    document.body.appendChild(toast);
    
    const toastEl = document.getElementById('suggestionToast');
    const bsToast = new bootstrap.Toast(toastEl);
    bsToast.show();
    
    // In a real application, we would update the form fields here
    // For example, adding new habit tracker items, changing the theme, etc.
}

// Function to add font size controls for better readability
function addFontSizeControls() {
    const controls = document.createElement('div');
    controls.className = 'font-size-controls';
    controls.innerHTML = `
        <button class="font-size-btn" id="increaseFontSize" title="Increase Font Size">
            <i class="fas fa-plus"></i>
        </button>
        <button class="font-size-btn" id="decreaseFontSize" title="Decrease Font Size">
            <i class="fas fa-minus"></i>
        </button>
        <button class="font-size-btn" id="resetFontSize" title="Reset Font Size">
            <i class="fas fa-undo"></i>
        </button>
    `;
    document.body.appendChild(controls);
    
    // Current font size level (0 = normal, 1 = large, 2 = larger)
    let fontSizeLevel = 0;
    
    // Check if user has a saved preference
    const savedFontSize = localStorage.getItem('fontSizeLevel');
    if (savedFontSize !== null) {
        fontSizeLevel = parseInt(savedFontSize);
        applyFontSize(fontSizeLevel);
    }
    
    // Add event listeners
    document.getElementById('increaseFontSize').addEventListener('click', function() {
        if (fontSizeLevel < 2) {
            fontSizeLevel++;
            applyFontSize(fontSizeLevel);
            localStorage.setItem('fontSizeLevel', fontSizeLevel);
        }
    });
    
    document.getElementById('decreaseFontSize').addEventListener('click', function() {
        if (fontSizeLevel > 0) {
            fontSizeLevel--;
            applyFontSize(fontSizeLevel);
            localStorage.setItem('fontSizeLevel', fontSizeLevel);
        }
    });
    
    document.getElementById('resetFontSize').addEventListener('click', function() {
        fontSizeLevel = 0;
        applyFontSize(fontSizeLevel);
        localStorage.setItem('fontSizeLevel', fontSizeLevel);
    });
    
    // Function to apply font size
    function applyFontSize(level) {
        document.body.classList.remove('font-size-large', 'font-size-larger');
        if (level === 1) {
            document.body.classList.add('font-size-large');
        } else if (level === 2) {
            document.body.classList.add('font-size-larger');
        }
    }
}

// Function to add high contrast mode toggle
function addHighContrastModeToggle() {
    // Add high contrast button next to style toggle
    const styleToggle = document.getElementById('styleToggle');
    if (styleToggle) {
        const contrastToggle = document.createElement('button');
        contrastToggle.className = 'style-toggle high-contrast-toggle';
        contrastToggle.id = 'contrastToggle';
        contrastToggle.title = 'Toggle high contrast mode';
        contrastToggle.innerHTML = '<i class="fas fa-adjust"></i>';
        contrastToggle.style.bottom = '80px';
        
        document.body.appendChild(contrastToggle);
        
        // Check if user has a saved preference
        const savedHighContrast = localStorage.getItem('high-contrast-mode') === 'true';
        if (savedHighContrast) {
            document.body.classList.add('high-contrast-mode');
        }
        
        // Add event listener
        contrastToggle.addEventListener('click', function() {
            document.body.classList.toggle('high-contrast-mode');
            
            // Save preference
            const isHighContrast = document.body.classList.contains('high-contrast-mode');
            localStorage.setItem('high-contrast-mode', isHighContrast);
        });
    }
}

// Function to apply a template
function applyTemplate(templateType) {
    // This would normally pre-fill the form based on the selected template
    // For now, we'll just simulate it by showing a toast notification
    
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '11';
    toast.innerHTML = `
        <div id="templateToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto"><i class="fas fa-th-large me-2"></i>Template Applied</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                The ${templateType} template has been applied to your planner.
            </div>
        </div>
    `;
    document.body.appendChild(toast);
    
    const toastEl = document.getElementById('templateToast');
    const bsToast = new bootstrap.Toast(toastEl);
    bsToast.show();
    
    // In a real application, we would update the form fields here based on the template
    // For example, setting specific habits, components, and styles
    
    // Simulate updating the form with template data
    switch(templateType) {
        case 'student':
            if (document.getElementById('habits')) {
                document.getElementById('habits').value = 'Study, Attend class, Complete assignments, Review notes';
            }
            if (document.getElementById('theme')) {
                document.getElementById('theme').value = 'Academic Success';
            }
            break;
        case 'work':
            if (document.getElementById('habits')) {
                document.getElementById('habits').value = 'Email management, Meeting preparation, Project tasks, Follow-ups';
            }
            if (document.getElementById('theme')) {
                document.getElementById('theme').value = 'Professional Growth';
            }
            break;
        case 'fitness':
            if (document.getElementById('habits')) {
                document.getElementById('habits').value = 'Exercise, Water intake, Protein intake, Sleep 8 hours';
            }
            if (document.getElementById('theme')) {
                document.getElementById('theme').value = 'Health & Fitness';
            }
            break;
        case 'creative':
            if (document.getElementById('habits')) {
                document.getElementById('habits').value = 'Daily creation, Idea journaling, Research, Skill practice';
            }
            if (document.getElementById('theme')) {
                document.getElementById('theme').value = 'Creative Expression';
            }
            break;
        case 'mindfulness':
            if (document.getElementById('habits')) {
                document.getElementById('habits').value = 'Meditation, Gratitude, Deep breathing, Journaling';
            }
            if (document.getElementById('theme')) {
                document.getElementById('theme').value = 'Mindfulness & Well-being';
            }
            break;
        case 'travel':
            if (document.getElementById('habits')) {
                document.getElementById('habits').value = 'Research destinations, Budget tracking, Packing list, Language practice';
            }
            if (document.getElementById('theme')) {
                document.getElementById('theme').value = 'Travel & Adventure';
            }
            break;
    }
    
    // Update style based on template
    if (document.getElementById('style')) {
        const styleSelect = document.getElementById('style');
        switch(templateType) {
            case 'student':
            case 'work':
                styleSelect.value = 'minimalist';
                break;
            case 'fitness':
            case 'travel':
                styleSelect.value = 'colorful';
                break;
            case 'creative':
            case 'mindfulness':
                styleSelect.value = 'illustrated';
                break;
        }
        
        // Trigger change event to update preview
        const event = new Event('change');
        styleSelect.dispatchEvent(event);
    }
} 