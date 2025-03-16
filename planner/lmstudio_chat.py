import json
import re
from typing import Dict, List, Any, Optional, Tuple
from .lmstudio_tools import LMStudioToolsClient
from .chat_processor import ChatProcessor
from .config import Config

class LMStudioChat:
    """Chat interface for LM Studio."""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1", api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LM Studio chat interface.
        
        Args:
            base_url: The base URL for the LM Studio API
            api_key: Optional API key for authentication
            model: Optional model name to use
        """
        self.client = LMStudioToolsClient(base_url=base_url, api_key=api_key)
        self.processor = ChatProcessor()
        self.conversation_history = []
        self.model = model or Config.get_model('lmstudio') or 'local-model'
        
        # Add system message
        self.conversation_history.append({
            "role": "system",
            "content": (
                "Ты - помощник для планирования задач и событий в ежедневнике. "
                "Твоя задача - помогать пользователю заполнять ежедневник, извлекая информацию из его сообщений. "
                "Отвечай кратко и по делу, фокусируясь на задачах планирования. "
                "Если пользователь просит добавить что-то в ежедневник, подтверди добавление и спроси, нужно ли добавить что-то еще. "
                "Если пользователь задает вопрос не связанный с планированием, вежливо напомни, что твоя основная задача - помогать с ежедневником."
            )
        })
    
    def process_message(self, message: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Process a user message and generate a response.
        
        Args:
            message: The user message
            
        Returns:
            A tuple containing:
            - A list of extracted planner items
            - A response message
        """
        # First try to extract planner items using pattern matching
        items, pattern_response = self.processor.process_message(message)
        
        # If items were extracted, use the pattern-based response
        if items:
            # Add the message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message
            })
            
            self.conversation_history.append({
                "role": "assistant",
                "content": pattern_response
            })
            
            return items, pattern_response
        
        # If no items were extracted, use LM Studio to generate a response
        return self.process_with_lmstudio(message)
    
    def process_with_lmstudio(self, message: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Process a message using LM Studio.
        
        Args:
            message: The user message
            
        Returns:
            A tuple containing:
            - A list of extracted planner items
            - A response message
        """
        # Add the message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Define the tools for planner items
        planner_tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_planner_items",
                    "description": "Add items to the planner based on user request",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["event", "task", "note"],
                                            "description": "Type of planner item"
                                        },
                                        "title": {
                                            "type": "string",
                                            "description": "Title of the planner item"
                                        },
                                        "time": {
                                            "type": "string",
                                            "description": "Time of the event in HH:MM format (only for events)"
                                        },
                                        "description": {
                                            "type": "string",
                                            "description": "Optional description of the planner item"
                                        }
                                    },
                                    "required": ["type", "title"]
                                }
                            }
                        },
                        "required": ["items"]
                    }
                }
            }
        ]
        
        # Send the request to LM Studio
        response = self.client.chat_completion(
            messages=self.conversation_history,
            tools=planner_tools,
            model=self.model
        )
        
        # Process the response
        items = []
        response_text = ""
        
        if "choices" in response and response["choices"] and "message" in response["choices"][0]:
            message = response["choices"][0]["message"]
            
            # If the model used a tool
            if "tool_calls" in message and message["tool_calls"]:
                tool_call = message["tool_calls"][0]
                if tool_call["function"]["name"] == "add_planner_items":
                    try:
                        tool_args = json.loads(tool_call["function"]["arguments"])
                        items = tool_args.get("items", [])
                        
                        # Generate a response based on the items
                        response_text = self.processor.generate_response("", items)
                    except json.JSONDecodeError:
                        response_text = "Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз."
            
            # If the model didn't use a tool but provided a response
            if not response_text and "content" in message and message["content"]:
                response_text = message["content"]
        
        # If no response was generated, use a default response
        if not response_text:
            response_text = "Извините, я не смог обработать ваш запрос. Пожалуйста, попробуйте сформулировать его иначе."
        
        # Add the response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })
        
        # Keep conversation history manageable (last 10 messages)
        if len(self.conversation_history) > 12:  # system message + 10 exchanges
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-10:]
        
        return items, response_text 