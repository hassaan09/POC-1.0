"""
Processes tasks and breaks them down into actionable steps
"""
import re
from typing import Dict, List, Any, Optional
from src.ui_tree_manager import UITreeManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'task_processor.log')

class TaskProcessor:
    def __init__(self):
        self.ui_tree_manager = UITreeManager()
        
    def process_user_input(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Process user input and return task execution plan"""
        try:
            logger.info(f"Processing user input: {user_input}")
            
            # Find matching task template
            matching_task = self.ui_tree_manager.find_best_matching_task(user_input)
            
            if not matching_task:
                logger.warning("No matching task found")
                return None
            
            # Get task steps
            steps = self.ui_tree_manager.get_task_steps(matching_task['task_id'])
            
            if not steps:
                logger.warning(f"No steps found for task {matching_task['task_id']}")
                return None
            
            # Extract dynamic values from user input
            dynamic_values = self.extract_dynamic_values(user_input, matching_task)
            
            # Create execution plan
            execution_plan = {
                'task_info': matching_task,
                'steps': steps,
                'dynamic_values': dynamic_values,
                'status': 'ready'
            }
            
            logger.info(f"Task execution plan created for: {matching_task['task_name']}")
            return execution_plan
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return None
    
    def extract_dynamic_values(self, user_input: str, task_info: Dict[str, Any]) -> Dict[str, str]:
        """Extract dynamic values from user input based on task type"""
        dynamic_values = {}
        
        try:
            task_id = task_info.get('task_id', '')
            
            if task_id == 'email_compose':
                # Extract email address
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, user_input)
                if emails:
                    dynamic_values['recipient_email'] = emails[0]
                
                # Extract subject (look for keywords like "regarding", "about", "subject")
                subject_patterns = [
                    r'regarding\s+(.+?)(?:\s+to\s+|\s*$)',
                    r'about\s+(.+?)(?:\s+to\s+|\s*$)',
                    r'subject\s+(.+?)(?:\s+to\s+|\s*$)'
                ]
                
                for pattern in subject_patterns:
                    match = re.search(pattern, user_input, re.IGNORECASE)
                    if match:
                        dynamic_values['email_subject'] = match.group(1).strip()
                        break
                
                # If no specific subject found, use a generic one
                if 'email_subject' not in dynamic_values:
                    dynamic_values['email_subject'] = "Inquiry"
            
            elif task_id == 'web_search':
                # Extract search query (everything after common search keywords)
                search_patterns = [
                    r'search\s+(?:for\s+)?(.+)',
                    r'find\s+(?:information\s+about\s+)?(.+)',
                    r'look\s+(?:up\s+)?(.+)',
                    r'google\s+(.+)'
                ]
                
                for pattern in search_patterns:
                    match = re.search(pattern, user_input, re.IGNORECASE)
                    if match:
                        dynamic_values['search_query'] = match.group(1).strip()
                        break
                
                # If no pattern matched, use the entire input as search query
                if 'search_query' not in dynamic_values:
                    dynamic_values['search_query'] = user_input
            
            elif task_id == 'web_navigate':
                # Extract URL or website name
                url_pattern = r'https?://[^\s]+'
                urls = re.findall(url_pattern, user_input)
                if urls:
                    dynamic_values['target_url'] = urls[0]
                else:
                    # Look for website names
                    website_patterns = [
                        r'(?:go\s+to\s+|visit\s+|open\s+)([^\s]+\.com|[^\s]+\.org|[^\s]+\.net)',
                        r'([^\s]+\.com|[^\s]+\.org|[^\s]+\.net)'
                    ]
                    
                    for pattern in website_patterns:
                        match = re.search(pattern, user_input, re.IGNORECASE)
                        if match:
                            website = match.group(1)
                            if not website.startswith('http'):
                                website = f'https://{website}'
                            dynamic_values['target_url'] = website
                            break
            
            logger.info(f"Extracted dynamic values: {dynamic_values}")
            
        except Exception as e:
            logger.error(f"Error extracting dynamic values: {e}")
        
        return dynamic_values
