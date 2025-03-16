import json
import requests
from typing import Dict, List, Any, Optional

class LMStudioToolsClient:
    """Client for interacting with LM Studio API with tool use functionality."""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1", api_key: Optional[str] = None):
        """
        Initialize the LM Studio client.
        
        Args:
            base_url: The base URL for the LM Studio API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key and api_key.strip():
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def chat_completion(self, 
                        messages: List[Dict[str, str]], 
                        model: str = "local-model",
                        tools: Optional[List[Dict[str, Any]]] = None,
                        temperature: float = 0.7,
                        max_tokens: int = 1024) -> Dict[str, Any]:
        """
        Send a chat completion request to LM Studio.
        
        Args:
            messages: List of message objects with role and content
            model: The model to use
            tools: Optional list of tools to make available to the model
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The response from the API
        """
        endpoint = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": str(e)
            }
    
    def get_planner_suggestions(self, prompt: str, model: str = "local-model") -> Dict[str, Any]:
        """
        Get planner suggestions using tool use functionality.
        
        Args:
            prompt: The user prompt
            model: The model to use
            
        Returns:
            Suggestions for planner components
        """
        # Define the tools for planner suggestions
        planner_tools = [
            {
                "type": "function",
                "function": {
                    "name": "suggest_planner_components",
                    "description": "Suggest planner components based on user needs and preferences",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "components": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of suggested planner components"
                            },
                            "explanation": {
                                "type": "string",
                                "description": "Explanation of why these components are suggested"
                            },
                            "theme": {
                                "type": "string",
                                "description": "Suggested theme for the planner"
                            },
                            "style": {
                                "type": "string",
                                "enum": ["minimalist", "colorful", "illustrated"],
                                "description": "Suggested visual style for the planner"
                            }
                        },
                        "required": ["components", "explanation"]
                    }
                }
            }
        ]
        
        # Create messages for the chat
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that suggests planner components based on user needs. Use the suggest_planner_components function to provide structured suggestions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Send the request
        response = self.chat_completion(
            messages=messages,
            model=model,
            tools=planner_tools
        )
        
        # Process the response
        if "error" in response:
            return {
                "success": False,
                "message": response["message"]
            }
        
        # Check if the model used a tool
        if "choices" in response and response["choices"] and "message" in response["choices"][0]:
            message = response["choices"][0]["message"]
            
            # If the model used a tool
            if "tool_calls" in message and message["tool_calls"]:
                tool_call = message["tool_calls"][0]
                if tool_call["function"]["name"] == "suggest_planner_components":
                    try:
                        suggestions = json.loads(tool_call["function"]["arguments"])
                        return {
                            "success": True,
                            "suggestions": suggestions
                        }
                    except json.JSONDecodeError:
                        return {
                            "success": False,
                            "message": "Failed to parse tool call arguments"
                        }
            
            # If the model didn't use a tool but provided a response
            if "content" in message and message["content"]:
                return {
                    "success": True,
                    "message": message["content"]
                }
        
        return {
            "success": False,
            "message": "No valid response from the model"
        } 