/**
 * Main JavaScript for Personal Planner Generator
 * Handles general UI interactions and functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Password visibility toggle
    const togglePasswordBtns = document.querySelectorAll('.toggle-password');
    togglePasswordBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = document.querySelector(this.getAttribute('data-target'));
            if (input) {
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                
                // Toggle icon
                const icon = this.querySelector('i');
                if (icon) {
                    if (type === 'text') {
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                    } else {
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                    }
                }
            }
        });
    });
    
    // API Key form submission
    const apiKeyForms = document.querySelectorAll('.api-key-form');
    apiKeyForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const provider = this.getAttribute('data-provider');
            const apiKeyInput = this.querySelector('.api-key-input');
            const baseUrlInput = this.querySelector('.base-url-input');
            const modelSelect = this.querySelector('.model-select');
            const submitBtn = this.querySelector('button[type="submit"]');
            const statusElement = this.querySelector('.api-key-status');
            
            if (!provider || !apiKeyInput) return;
            
            const apiKey = apiKeyInput.value.trim();
            const baseUrl = baseUrlInput ? baseUrlInput.value.trim() : '';
            const model = modelSelect ? modelSelect.value : '';
            
            if (!apiKey) {
                showFormError(statusElement, 'API key cannot be empty');
                return;
            }
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
            
            // Create request payload
            const payload = {
                provider: provider,
                api_key: apiKey
            };
            
            if (baseUrl) {
                payload.base_url = baseUrl;
            }
            
            if (model) {
                payload.model = model;
            }
            
            // Save API key
            fetch('/api/settings/save-key', {
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
                showFormSuccess(statusElement, data.message || 'API key saved successfully');
                
                // Reset form state
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Save';
                
                // Refresh page after short delay to update UI
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            })
            .catch(error => {
                console.error('Error saving API key:', error);
                showFormError(statusElement, error.message || 'Error saving API key');
                
                // Reset form state
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Save';
            });
        });
    });
    
    // Test API Key buttons
    const testApiKeyBtns = document.querySelectorAll('.test-api-key');
    testApiKeyBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const provider = this.getAttribute('data-provider');
            const form = this.closest('.api-key-form');
            const apiKeyInput = form.querySelector('.api-key-input');
            const baseUrlInput = form.querySelector('.base-url-input');
            const statusElement = form.querySelector('.api-key-status');
            
            if (!provider || !apiKeyInput) return;
            
            const apiKey = apiKeyInput.value.trim();
            const baseUrl = baseUrlInput ? baseUrlInput.value.trim() : '';
            
            if (!apiKey) {
                showFormError(statusElement, 'API key cannot be empty');
                return;
            }
            
            // Show loading state
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Testing...';
            
            // Test API key using the AI Model Manager
            if (window.aiModelManager) {
                window.aiModelManager.testApiKey(provider, apiKey, baseUrl, function(result) {
                    if (result.success) {
                        showFormSuccess(statusElement, result.message || 'API key is valid');
                    } else {
                        showFormError(statusElement, result.error || 'API key is invalid');
                    }
                    
                    // Reset button state
                    btn.disabled = false;
                    btn.innerHTML = 'Test';
                });
            } else {
                // Fallback if AI Model Manager is not available
                fetch('/api/settings/test-key', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        provider: provider,
                        api_key: apiKey,
                        base_url: baseUrl
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    showFormSuccess(statusElement, data.message || 'API key is valid');
                    
                    // Reset button state
                    btn.disabled = false;
                    btn.innerHTML = 'Test';
                })
                .catch(error => {
                    console.error('Error testing API key:', error);
                    showFormError(statusElement, error.message || 'Error testing API key');
                    
                    // Reset button state
                    btn.disabled = false;
                    btn.innerHTML = 'Test';
                });
            }
        });
    });
    
    // Language selection buttons
    const languageBtns = document.querySelectorAll('.language-btn');
    languageBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const language = this.getAttribute('data-language');
            if (!language) return;
            
            // Redirect to language change route
            window.location.href = `/language/${language}`;
        });
    });
    
    // Theme selection buttons
    const themeBtns = document.querySelectorAll('.theme-btn');
    themeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const theme = this.getAttribute('data-theme');
            if (!theme) return;
            
            // Update active state
            themeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Save theme preference
            localStorage.setItem('theme', theme);
            
            // Apply theme
            document.body.classList.remove('theme-light', 'theme-dark');
            document.body.classList.add(`theme-${theme}`);
            
            // Update theme toggle button icon
            const themeToggle = document.getElementById('themeToggle');
            if (themeToggle) {
                if (theme === 'dark') {
                    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
                } else {
                    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
                }
            }
        });
    });
    
    // Helper function to show form success message
    function showFormSuccess(element, message) {
        if (!element) return;
        
        element.innerHTML = `
            <div class="alert alert-success mt-2 mb-0">
                <i class="fas fa-check-circle me-2"></i> ${message}
            </div>
        `;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            element.innerHTML = '';
        }, 5000);
    }
    
    // Helper function to show form error message
    function showFormError(element, message) {
        if (!element) return;
        
        element.innerHTML = `
            <div class="alert alert-danger mt-2 mb-0">
                <i class="fas fa-exclamation-circle me-2"></i> ${message}
            </div>
        `;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            element.innerHTML = '';
        }, 5000);
    }
    
    // Function to show toast notifications
    window.showToast = function(message, type = 'primary') {
        const toastContainer = document.createElement('div');
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1050';
        
        toastContainer.innerHTML = `
            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-${type} text-white">
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        document.body.appendChild(toastContainer);
        const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'));
        toast.show();
        
        // Remove toast container after it's hidden
        toastContainer.querySelector('.toast').addEventListener('hidden.bs.toast', function() {
            toastContainer.remove();
        });
    };
}); 