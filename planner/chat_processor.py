import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

class ChatProcessor:
    """Processor for chat messages to extract planner items."""
    
    def __init__(self):
        """Initialize the chat processor."""
        self.current_date = datetime.now()
    
    def process_message(self, message: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Process a user message to extract planner items.
        
        Args:
            message: The user message
            
        Returns:
            A tuple containing:
            - A list of extracted planner items
            - A response message
        """
        # Extract time expressions
        items = self.extract_planner_items(message)
        
        # Generate response
        response = self.generate_response(message, items)
        
        return items, response
    
    def extract_planner_items(self, message: str) -> List[Dict[str, Any]]:
        """
        Extract planner items from a message.
        
        Args:
            message: The user message
            
        Returns:
            A list of planner items
        """
        items = []
        
        # Extract events with time
        event_patterns = [
            r'(?:запланировать|добавить|запланируй|добавь|создать|создай)\s+(?:встречу|событие|мероприятие|звонок|созвон|совещание)\s+(?:с|по|на тему)?\s+([^в]+?)\s+(?:в|на)\s+(\d{1,2}[:.]\d{2})',
            r'(?:встреча|событие|мероприятие|звонок|созвон|совещание)\s+(?:с|по|на тему)?\s+([^в]+?)\s+(?:в|на)\s+(\d{1,2}[:.]\d{2})',
        ]
        
        for pattern in event_patterns:
            matches = re.finditer(pattern, message.lower())
            for match in matches:
                title = match.group(1).strip()
                time_str = match.group(2).replace('.', ':')
                
                # Add leading zero if needed
                if ':' in time_str and len(time_str.split(':')[0]) == 1:
                    time_str = f"0{time_str}"
                
                items.append({
                    'type': 'event',
                    'title': title.capitalize(),
                    'time': time_str,
                    'description': ''
                })
        
        # Extract tasks
        task_patterns = [
            r'(?:добавить|добавь|создать|создай)\s+(?:задачу|задание|дело|пункт)\s*(?::|-)?\s*([^на]+?)(?:\s+на\s+|$)',
            r'(?:напомни(?:ть)?|не забыть)\s+(?:про|о|об|)?\s*([^на]+?)(?:\s+на\s+|$)',
        ]
        
        for pattern in task_patterns:
            matches = re.finditer(pattern, message.lower())
            for match in matches:
                title = match.group(1).strip()
                
                items.append({
                    'type': 'task',
                    'title': title.capitalize(),
                    'time': None,
                    'description': ''
                })
        
        # Extract notes
        note_patterns = [
            r'(?:добавить|добавь|создать|создай)\s+(?:заметку|запись|примечание)\s*(?::|-)?\s*([^на]+?)(?:\s+на\s+|$)',
        ]
        
        for pattern in note_patterns:
            matches = re.finditer(pattern, message.lower())
            for match in matches:
                title = match.group(1).strip()
                
                items.append({
                    'type': 'note',
                    'title': title.capitalize(),
                    'time': None,
                    'description': ''
                })
        
        # If no items were extracted but the message seems like a task
        if not items and len(message.split()) >= 2 and not message.lower().startswith(('что', 'как', 'почему', 'где', 'когда', 'кто', 'привет', 'здравствуй')):
            items.append({
                'type': 'task',
                'title': message.capitalize(),
                'time': None,
                'description': ''
            })
        
        return items
    
    def generate_response(self, message: str, items: List[Dict[str, Any]]) -> str:
        """
        Generate a response based on the message and extracted items.
        
        Args:
            message: The user message
            items: The extracted planner items
            
        Returns:
            A response message
        """
        if not items:
            return "Я не смог определить, что нужно добавить в ежедневник. Пожалуйста, уточните, что вы хотите запланировать. Например: 'Добавь встречу с Иваном в 15:00' или 'Напомни купить молоко'."
        
        response = "Я добавил в ваш ежедневник:\n\n"
        
        for item in items:
            if item['type'] == 'event':
                response += f"📅 **Событие**: {item['title']}"
                if item['time']:
                    response += f" в {item['time']}"
                response += "\n"
            elif item['type'] == 'task':
                response += f"✅ **Задача**: {item['title']}\n"
            elif item['type'] == 'note':
                response += f"📝 **Заметка**: {item['title']}\n"
        
        response += "\nЧто-нибудь еще добавить в ежедневник?"
        
        return response 