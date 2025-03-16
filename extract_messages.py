#!/usr/bin/env python
"""
Extract translatable strings from the Personal Planner Generator application.
This script extracts strings from Python files and Jinja2 templates for translation.
"""

import os
import subprocess
import sys

def extract_messages():
    """Extract translatable strings from Python files and templates."""
    print("Extracting translatable strings...")
    
    # Define the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if babel.cfg exists
    babel_cfg = os.path.join(base_dir, 'babel.cfg')
    if not os.path.exists(babel_cfg):
        print(f"Error: Babel configuration file not found at {babel_cfg}")
        return False
    
    # Create the pot file
    pot_file = os.path.join(base_dir, 'messages.pot')
    
    try:
        # Use pybabel to extract strings
        cmd = [
            'pybabel', 'extract',
            '-F', babel_cfg,
            '--keywords=_',
            '--keywords=gettext',
            '--keywords=ngettext',
            '--output', pot_file,
            '.'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error extracting messages: {result.stderr}")
            return False
        
        print(f"Successfully extracted messages to {pot_file}")
        
        # Update existing translation files
        for lang in ['en', 'ru']:
            lang_dir = os.path.join(base_dir, 'translations', lang, 'LC_MESSAGES')
            po_file = os.path.join(lang_dir, 'messages.po')
            
            # Create directory if it doesn't exist
            os.makedirs(lang_dir, exist_ok=True)
            
            if os.path.exists(po_file):
                # Update existing translation file
                cmd = [
                    'pybabel', 'update',
                    '-i', pot_file,
                    '-d', os.path.join(base_dir, 'translations'),
                    '-l', lang
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Error updating translations for {lang}: {result.stderr}")
                else:
                    print(f"Successfully updated translations for {lang}")
            else:
                # Initialize new translation file
                cmd = [
                    'pybabel', 'init',
                    '-i', pot_file,
                    '-d', os.path.join(base_dir, 'translations'),
                    '-l', lang
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Error initializing translations for {lang}: {result.stderr}")
                else:
                    print(f"Successfully initialized translations for {lang}")
        
        return True
    except Exception as e:
        print(f"Exception while extracting messages: {str(e)}")
        return False

if __name__ == "__main__":
    if extract_messages():
        print("All messages extracted successfully.")
        sys.exit(0)
    else:
        print("There were errors extracting messages.")
        sys.exit(1) 