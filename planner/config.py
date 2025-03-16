import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration settings for the application."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    
    # API keys (optional)
    OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY', '')
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
    
    # Ensure directories exist
    for folder in [UPLOAD_FOLDER, TEMP_FOLDER, OUTPUT_FOLDER]:
        os.makedirs(folder, exist_ok=True)
    
    # API Keys configuration file
    API_KEYS_FILE = os.path.join(BASE_DIR, 'api_keys.json')
    
    # Default language (en or ru)
    DEFAULT_LANGUAGE = 'en'
    
    # Available languages
    LANGUAGES = {
        'en': 'English',
        'ru': 'Русский'
    }
    
    # AI Models configuration
    AI_MODELS = {
        'openai': {
            'name': 'OpenAI (ChatGPT)',
            'icon': 'fa-comment-dots',
            'color': '#10a37f',
            'requires_key': True,
            'key_name': 'openai_api_key',
            'base_url_name': 'openai_base_url',
            'default_base_url': 'https://api.openai.com/v1',
            'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']
        },
        'anthropic': {
            'name': 'Anthropic (Claude)',
            'icon': 'fa-feather-alt',
            'color': '#6c63ff',
            'requires_key': True,
            'key_name': 'anthropic_api_key',
            'models': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
        },
        'google': {
            'name': 'Google (Gemini)',
            'icon': 'fa-brain',
            'color': '#4285f4',
            'requires_key': True,
            'key_name': 'google_api_key',
            'models': ['gemini-pro', 'gemini-ultra']
        },
        'lmstudio': {
            'name': 'LM Studio (Local)',
            'icon': 'fa-laptop-code',
            'color': '#ff9800',
            'requires_key': False,
            'key_name': 'lmstudio_api_key',
            'base_url_name': 'lmstudio_base_url',
            'default_base_url': 'http://127.0.0.1:1234/v1',
            'models': ['local-model', 'mistral-7b', 'llama-2-7b', 'llama-2-13b', 'llama-2-70b', 'mixtral-8x7b', 'phi-2', 'gemma-7b', 'gemma-2b']
        }
    }
    
    # Planner styles
    STYLES = {
        'minimalist': {
            'font': 'Helvetica',
            'primary_color': '#333333',
            'secondary_color': '#666666',
            'background_color': '#FFFFFF',
            'accent_color': '#4A90E2'
        },
        'colorful': {
            'font': 'Helvetica',
            'primary_color': '#2C3E50',
            'secondary_color': '#E74C3C',
            'background_color': '#ECF0F1',
            'accent_color': '#3498DB'
        },
        'illustrated': {
            'font': 'Helvetica',
            'primary_color': '#34495E',
            'secondary_color': '#16A085',
            'background_color': '#F5F5F5',
            'accent_color': '#E67E22'
        }
    }
    
    # Quotable API for inspirational quotes
    QUOTABLE_API_URL = 'https://api.quotable.io/random'
    
    # OpenWeatherMap API for weather forecasts
    OPENWEATHERMAP_API_URL = 'https://api.openweathermap.org/data/2.5/forecast'
    
    @classmethod
    def get_api_keys(cls):
        """Get all stored API keys"""
        if os.path.exists(cls.API_KEYS_FILE):
            try:
                with open(cls.API_KEYS_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @classmethod
    def save_api_key(cls, provider, api_key, base_url=None, model=None):
        """Save an API key for a provider"""
        api_keys = cls.get_api_keys()
        
        # Get the key name from the provider configuration
        provider_config = cls.AI_MODELS.get(provider, {})
        key_name = provider_config.get('key_name')
        
        if key_name:
            api_keys[key_name] = api_key
            
            # Save base URL if provided and supported
            if base_url and 'base_url_name' in provider_config:
                api_keys[provider_config['base_url_name']] = base_url
            
            # Save model if provided
            if model:
                api_keys[f"{provider}_model"] = model
            
            with open(cls.API_KEYS_FILE, 'w') as f:
                json.dump(api_keys, f)
            
            return True
        return False
    
    @classmethod
    def get_api_key(cls, provider):
        """Get API key for a specific provider"""
        api_keys = cls.get_api_keys()
        provider_config = cls.AI_MODELS.get(provider, {})
        key_name = provider_config.get('key_name')
        
        if key_name and key_name in api_keys:
            return api_keys[key_name]
        return None
    
    @classmethod
    def get_model(cls, provider):
        """Get selected model for a specific provider"""
        api_keys = cls.get_api_keys()
        model_key = f"{provider}_model"
        
        if model_key in api_keys:
            return api_keys[model_key]
        
        # Return first model as default
        provider_config = cls.AI_MODELS.get(provider, {})
        if 'models' in provider_config and provider_config['models']:
            return provider_config['models'][0]
        
        return None
    
    @classmethod
    def get_base_url(cls, provider):
        """Get base URL for a specific provider"""
        api_keys = cls.get_api_keys()
        provider_config = cls.AI_MODELS.get(provider, {})
        base_url_name = provider_config.get('base_url_name')
        
        if base_url_name and base_url_name in api_keys:
            return api_keys[base_url_name]
        return provider_config.get('default_base_url', '')
    
    @classmethod
    def is_api_key_set(cls, provider):
        """Check if API key is set for a provider"""
        provider_config = cls.AI_MODELS.get(provider, {})
        
        # If provider doesn't require a key, return True
        if not provider_config.get('requires_key', True):
            return True
            
        return cls.get_api_key(provider) is not None 