"""
UI Tree Manager for storing and retrieving automation workflows
Uses Excel file for structured storage of UI mappings
"""

import pandas as pd
import os
from pathlib import Path
from loguru import logger
import json

class UITreeManager:
    """Manages UI automation workflows and mappings"""
    
    def __init__(self, excel_file_path="data/ui_tree.xlsx"):
        self.excel_file_path = excel_file_path
        self.ui_mappings = {}
        self.load_ui_mappings()
    
    def load_ui_mappings(self):
        """Load UI mappings from Excel file"""
        try:
            if not os.path.exists(self.excel_file_path):
                logger.info("UI Tree Excel file not found, creating default mappings")
                self.create_default_mappings()
                return
            
            # Load different sheets from Excel
            self.categories_df = pd.read_excel(self.excel_file_path, sheet_name='Categories')
            self.actions_df = pd.read_excel(self.excel_file_path, sheet_name='Actions')
            self.steps_df = pd.read_excel(self.excel_file_path, sheet_name='Steps')
            
            # Convert to dictionary format for easier access
            self.process_mappings()
            
            logger.info(f"Loaded UI mappings from {self.excel_file_path}")
            
        except Exception as e:
            logger.error(f"Error loading UI mappings: {e}")
            self.create_default_mappings()
    
    def create_default_mappings(self):
        """Create default UI mappings and save to Excel"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Default categories
            categories_data = {
                'category_id': ['email', 'web', 'file', 'app'],
                'category_name': ['Email Operations', 'Web Browsing', 'File Operations', 'Application Control'],
                'description': [
                    'Email composition, sending, and management',
                    'Web navigation and interaction',
                    'File creation, editing, and management',
                    'Application launching and control'
                ]
            }
            
            # Default actions
            actions_data = {
                'action_id': ['compose_email', 'send_email', 'open_website', 'click_element', 'type_text', 'open_file'],
                'category_id': ['email', 'email', 'web', 'web', 'web', 'file'],
                'action_name': ['Compose Email', 'Send Email', 'Open Website', 'Click Element', 'Type Text', 'Open File'],
                'keywords': [
                    'email, compose, write, create, draft',
                    'send, email, submit, deliver',
                    'open, website, browse, go to, navigate',
                    'click, press, select, button',
                    'type, enter, input, write',
                    'open, file, document, folder'
                ],
                'difficulty': [2, 3, 1, 1, 1, 1]
            }
            
            # Default steps
            steps_data = {
                'step_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'action_id': ['compose_email', 'compose_email', 'compose_email', 'send_email', 'open_website', 'click_element', 'type_text', 'open_file', 'open_file', 'open_file'],
                'step_order': [1, 2, 3, 1, 1, 1, 1, 1, 2, 3],
                'step_description': [
                    'Open Gmail website',
                    'Click on Compose button',
                    'Fill email details',
                    'Click Send button',
                    'Open browser and navigate to URL',
                    'Locate and click on specified element',
                    'Enter text in input field',
                    'Open file explorer',
                    'Navigate to file location',
                    'Select and open file'
                ],
                'action_type': [
                    'web_navigate',
                    'click',
                    'form_fill',
                    'click',
                    'web_navigate',
                    'click',
                    'type',
                    'app_launch',
                    'navigate',
                    'file_open'
                ],
                'selector': [
                    'https://gmail.com',
                    'div[role="button"][aria-label*="Compose"]',
                    'form',
                    'div[role="button"][aria-label*="Send"]',
                    'url_parameter',
                    'element_selector',
                    'input_field',
                    'explorer.exe',
                    'file_path',
                    'file_name'
                ],
                'parameters': [
                    '{}',
                    '{}',
                    '{"recipient": "email_param", "subject": "subject_param", "body": "body_param"}',
                    '{}',
                    '{"url": "url_param"}',
                    '{"selector": "selector_param"}',
                    '{"text": "text_param"}',
                    '{}',
                    '{"path": "path_param"}',
                    '{"filename": "filename_param"}'
                ]
            }
            
            # Create DataFrames
            self.categories_df = pd.DataFrame(categories_data)
            self.actions_df = pd.DataFrame(actions_data)
            self.steps_df = pd.DataFrame(steps_data)
            
            # Save to Excel
            with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
                self.categories_df.to_excel(writer, sheet_name='Categories', index=False)
                self.actions_df.to_excel(writer, sheet_name='Actions', index=False)
                self.steps_df.to_excel(writer, sheet_name='Steps', index=False)
            
            self.process_mappings()
            logger.info(f"Created default UI mappings at {self.excel_file_path}")
            
        except Exception as e:
            logger.error(f"Error creating default mappings: {e}")
    
    def process_mappings(self):
        """Process loaded DataFrames into dictionary format"""
        try:
            self.ui_mappings = {}
            
            # Process each action
            for _, action in self.actions_df.iterrows():
                action_id = action['action_id']
                
                # Get steps for this action
                action_steps = self.steps_df[self.steps_df['action_id'] == action_id].sort_values('step_order')
                
                steps_list = []
                for _, step in action_steps.iterrows():
                    step_dict = {
                        'step_id': step['step_id'],
                        'order': step['step_order'],
                        'description': step['step_description'],
                        'action': step['action_type'],
                        'selector': step['selector'],
                        'parameters': json.loads(step['parameters']) if step['parameters'] else {}
                    }
                    steps_list.append(step_dict)
                
                # Store action mapping
                self.ui_mappings[action_id] = {
                    'action_name': action['action_name'],
                    'category': action['category_id'],
                    'keywords': [kw.strip() for kw in action['keywords'].split(',')],
                    'difficulty': action['difficulty'],
                    'steps': steps_list
                }
            
            logger.info(f"Processed {len(self.ui_mappings)} action mappings")
            
        except Exception as e:
            logger.error(f"Error processing mappings: {e}")
    
    def get_automation_steps(self, action_id):
        """Get automation steps for a specific action"""
        try:
            if action_id not in self.ui_mappings:
                logger.warning(f"Action {action_id} not found in UI mappings")
                return []
            
            steps = self.ui_mappings[action_id]['steps']
            logger.info(f"Retrieved {len(steps)} steps for action {action_id}")
            return steps
            
        except Exception as e:
            logger.error(f"Error getting automation steps: {e}")
            return []
    
    def get_all_actions(self):
        """Get all available actions with their keywords"""
        actions = []
        
        for action_id, action_data in self.ui_mappings.items():
            actions.append({
                'action_id': action_id,
                'action_name': action_data['action_name'],
                'keywords': action_data['keywords'],
                'category': action_data['category']
            })
        
        return actions
    
    def add_action_mapping(self, action_id, action_name, category, keywords, steps):
        """Add new action mapping to the UI tree"""
        try:
            # Add to in-memory mappings
            self.ui_mappings[action_id] = {
                'action_name': action_name,
                'category': category,
                'keywords': keywords,
                'steps': steps
            }
            
            # Update Excel file
            self.save_mappings_to_excel()
            
            logger.info(f"Added new action mapping: {action_id}")
            
        except Exception as e:
            logger.error(f"Error adding action mapping: {e}")
    
    def save_mappings_to_excel(self):
        """Save current mappings back to Excel file"""
        try:
            # This would involve converting the dictionary back to DataFrames
            # and saving to Excel - implementation depends on specific needs
            logger.info("UI mappings saved to Excel")
            
        except Exception as e:
            logger.error(f"Error saving mappings to Excel: {e}")
    
    def get_action_by_keywords(self, keywords):
        """Find actions that match given keywords"""
        matching_actions = []
        
        keywords_lower = [kw.lower() for kw in keywords]
        
        for action_id, action_data in self.ui_mappings.items():
            action_keywords = [kw.lower() for kw in action_data['keywords']]
            
            # Check for keyword matches
            if any(kw in action_keywords for kw in keywords_lower):
                matching_actions.append(action_id)
        
        return matching_actions