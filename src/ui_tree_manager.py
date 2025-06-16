import os 
# src/ui_tree_manager.py
"""
Manages UI tree mappings and task definitions
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Optional, Tuple, Any
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'ui_tree_manager.log')

class UITreeManager:
    def __init__(self):
        self.ui_mappings = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.tfidf_matrix = None
        self.load_ui_mappings()
        
    def load_ui_mappings(self):
        """Load UI mappings from Excel file"""
        try:
            Config.ensure_directories()
            
            # Create default mappings if file doesn't exist
            if not os.path.exists(Config.UI_MAPPINGS_FILE):
                self.create_default_mappings()
            
            # Load the mappings
            self.ui_mappings = pd.read_excel(Config.UI_MAPPINGS_FILE, sheet_name=None)
            
            # Prepare TFIDF matrix for task matching
            self.prepare_tfidf_matrix()
            
            logger.info("UI mappings loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading UI mappings: {e}")
            self.create_default_mappings()
    
    def create_default_mappings(self):
        """Create default UI mappings Excel file"""
        try:
            # Categories sheet
            categories = pd.DataFrame({
                'category_id': ['email', 'web', 'file', 'app', 'search'],
                'category_name': ['Email Operations', 'Web Browsing', 'File Operations', 'Application Control', 'Search Operations'],
                'description': [
                    'Email composition, sending, and management',
                    'Web navigation and interaction',
                    'File creation, editing, and management',
                    'Application launching and control',
                    'Search and information retrieval'
                ]
            })
            
            # Task templates sheet
            task_templates = pd.DataFrame({
                'task_id': ['email_compose', 'web_search', 'web_navigate', 'file_create', 'app_open'],
                'category_id': ['email', 'search', 'web', 'file', 'app'],
                'task_name': ['Compose Email', 'Search Web', 'Navigate Website', 'Create File', 'Open Application'],
                'keywords': [
                    'email send compose mail message write',
                    'search google find look query',
                    'navigate website browse open visit go',
                    'create file new document write',
                    'open launch start application program'
                ],
                'description': [
                    'Compose and send an email',
                    'Search for information on the web',
                    'Navigate to a specific website',
                    'Create a new file or document',
                    'Open an application or program'
                ]
            })
            
            # Action steps sheet
            action_steps = pd.DataFrame({
                'step_id': ['email_1', 'email_2', 'email_3', 'search_1', 'search_2', 'nav_1', 'nav_2'],
                'task_id': ['email_compose', 'email_compose', 'email_compose', 'web_search', 'web_search', 'web_navigate', 'web_navigate'],
                'step_order': [1, 2, 3, 1, 2, 1, 2],
                'action_type': ['navigate', 'click', 'type', 'navigate', 'type', 'navigate', 'wait'],
                'target_element': ['url', 'compose_button', 'recipient_field', 'url', 'search_box', 'url', 'page_load'],
                'action_value': ['https://gmail.com', '', '', 'https://google.com', '', '', ''],
                'description': [
                    'Navigate to Gmail',
                    'Click compose button',
                    'Enter recipient email',
                    'Navigate to Google',
                    'Enter search query',
                    'Navigate to target website',
                    'Wait for page to load'
                ]
            })
            
            # Element selectors sheet
            element_selectors = pd.DataFrame({
                'element_id': ['compose_button', 'recipient_field', 'subject_field', 'message_body', 'send_button', 'search_box'],
                'selector_type': ['xpath', 'xpath', 'xpath', 'xpath', 'xpath', 'name'],
                'selector_value': [
                    '//div[@role="button" and contains(text(), "Compose")]',
                    '//input[@aria-label="To"]',
                    '//input[@name="subjectbox"]',
                    '//div[@aria-label="Message Body"]',
                    '//div[@role="button" and contains(text(), "Send")]',
                    'q'
                ],
                'description': [
                    'Gmail compose button',
                    'Email recipient field',
                    'Email subject field',
                    'Email message body',
                    'Send email button',
                    'Google search box'
                ]
            })
            
            # Save to Excel file
            with pd.ExcelWriter(Config.UI_MAPPINGS_FILE, engine='openpyxl') as writer:
                categories.to_excel(writer, sheet_name='categories', index=False)
                task_templates.to_excel(writer, sheet_name='task_templates', index=False)
                action_steps.to_excel(writer, sheet_name='action_steps', index=False)
                element_selectors.to_excel(writer, sheet_name='element_selectors', index=False)
            
            logger.info("Default UI mappings created")
            
        except Exception as e:
            logger.error(f"Error creating default mappings: {e}")
            raise
    
    def prepare_tfidf_matrix(self):
        """Prepare TFIDF matrix for task matching"""
        try:
            if 'task_templates' not in self.ui_mappings:
                raise ValueError("task_templates sheet not found in UI mappings")
            
            task_templates = self.ui_mappings['task_templates']
            
            # Combine task name, keywords, and description for better matching
            documents = []
            for _, row in task_templates.iterrows():
                doc = f"{row['task_name']} {row['keywords']} {row['description']}"
                documents.append(doc)
            
            if documents:
                self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
                logger.info(f"TFIDF matrix prepared with {len(documents)} documents")
            else:
                logger.warning("No documents found for TFIDF matrix")
                
        except Exception as e:
            logger.error(f"Error preparing TFIDF matrix: {e}")
            raise
    
    def find_best_matching_task(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Find the best matching task for user input"""
        try:
            if self.tfidf_matrix is None or self.ui_mappings is None:
                logger.error("TFIDF matrix or UI mappings not initialized")
                return None
            
            if 'task_templates' not in self.ui_mappings:
                logger.error("task_templates sheet not found")
                return None
            
            # Transform user input
            user_vector = self.tfidf_vectorizer.transform([user_input])
            
            # Calculate similarities
            similarities = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
            
            # Find best match
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[best_match_idx]
            
            logger.info(f"Best match similarity: {best_similarity}")
            
            if best_similarity < Config.TFIDF_MIN_SIMILARITY:
                logger.warning(f"Best match similarity {best_similarity} below threshold {Config.TFIDF_MIN_SIMILARITY}")
                return None
            
            # Get the matching task
            task_templates = self.ui_mappings['task_templates']
            best_task = task_templates.iloc[best_match_idx].to_dict()
            best_task['similarity_score'] = float(best_similarity)
            
            logger.info(f"Found matching task: {best_task['task_name']} (similarity: {best_similarity:.3f})")
            
            return best_task
            
        except Exception as e:
            logger.error(f"Error finding best matching task: {e}")
            return None
    
    def get_task_steps(self, task_id: str) -> List[Dict[str, Any]]:
        """Get action steps for a specific task"""
        try:
            if 'action_steps' not in self.ui_mappings:
                logger.error("action_steps sheet not found")
                return []
            
            action_steps = self.ui_mappings['action_steps']
            task_steps = action_steps[action_steps['task_id'] == task_id]
            task_steps = task_steps.sort_values('step_order')
            
            steps = task_steps.to_dict('records')
            logger.info(f"Retrieved {len(steps)} steps for task {task_id}")
            
            return steps
            
        except Exception as e:
            logger.error(f"Error getting task steps: {e}")
            return []
    
    def get_element_selector(self, element_id: str) -> Optional[Dict[str, str]]:
        """Get element selector information"""
        try:
            if 'element_selectors' not in self.ui_mappings:
                logger.error("element_selectors sheet not found")
                return None
            
            selectors = self.ui_mappings['element_selectors']
            element_info = selectors[selectors['element_id'] == element_id]
            
            if element_info.empty:
                logger.warning(f"Element selector not found: {element_id}")
                return None
            
            return element_info.iloc[0].to_dict()
            
        except Exception as e:
            logger.error(f"Error getting element selector: {e}")
            return None