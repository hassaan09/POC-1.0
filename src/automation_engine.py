# src/automation_engine.py
"""
Handles browser automation using Selenium
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from typing import Dict, List, Any, Optional, Callable
from src.ui_tree_manager import UITreeManager
from src.utils.config import Config
from src.utils.logger import setup_logger
import pandas as pd 
from selenium.webdriver.common.keys import Keys 


logger = setup_logger(__name__, 'automation_engine.log')

class AutomationEngine:
    def __init__(self, status_callback: Optional[Callable] = None):
        self.driver = None
        self.ui_tree_manager = UITreeManager()
        self.status_callback = status_callback
        self.current_step = 0
        self.total_steps = 0
        
    def update_status(self, message: str, step: int = None):
        """Update status and call callback if provided"""
        if step is not None:
            self.current_step = step
        
        status_msg = f"Step {self.current_step}/{self.total_steps}: {message}"
        logger.info(status_msg)
        
        if self.status_callback:
            self.status_callback(status_msg)
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Setup Chrome driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configure driver
            self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
            self.driver.maximize_window()
            
            # Execute script to remove automation indicators
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome WebDriver setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            raise
    
    def execute_task(self, execution_plan: Dict[str, Any]) -> bool:
        """Execute a task based on execution plan"""
        try:
            if not execution_plan or execution_plan.get('status') != 'ready':
                logger.error("Invalid execution plan")
                return False
            
            steps = execution_plan.get('steps', [])
            dynamic_values = execution_plan.get('dynamic_values', {})
            task_info = execution_plan.get('task_info', {})
            
            if not steps:
                logger.error("No steps found in execution plan")
                return False
            
            self.total_steps = len(steps)
            self.current_step = 0
            
            # Setup driver
            self.update_status("Setting up browser...")
            self.setup_driver()
            
            # Execute each step
            for i, step in enumerate(steps, 1):
                self.update_status(f"Executing: {step.get('description', 'Unknown step')}", i)
                
                success = self.execute_step(step, dynamic_values, task_info)
                if not success:
                    logger.error(f"Step {i} failed: {step}")
                    return False
                
                # Small delay between steps
                time.sleep(1)
            
            self.update_status("Task completed successfully!")
            logger.info("Task execution completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            self.update_status(f"Error: {str(e)}")
            return False
        finally:
            # Keep browser open for demonstration
            if self.driver:
                self.update_status("Task finished - browser remains open for review")
    
    def execute_step(self, step: Dict[str, Any], dynamic_values: Dict[str, str], task_info: Dict[str, Any]) -> bool:
        """Execute a single step"""
        try:
            action_type = step.get('action_type', '').lower()
            target_element = step.get('target_element', '')

            action_value_raw = step.get('action_value', '')

            # Convert NaN or None to an empty string; otherwise, ensure it's a string
            if pd.isna(action_value_raw) or action_value_raw is None:
                action_value = ''
            else:
                action_value = str(action_value_raw)
            
            # Replace dynamic values in action_value
            if action_value:
                for key, value in dynamic_values.items():
                    action_value = action_value.replace(f'{{{key}}}', value)
            
            if action_type == 'navigate':
                return self.navigate_to_url(action_value or target_element)
            
            elif action_type == 'click':
                return self.click_element(target_element)
            
            elif action_type == 'type':
                # Determine what to type based on the target element and dynamic values
                text_to_type = self.get_text_to_type(target_element, dynamic_values, action_value)
                return self.type_text(target_element, text_to_type)
            
            elif action_type == 'wait':
                wait_time = int(action_value) if action_value.isdigit() else 3
                time.sleep(wait_time)
                return True
            
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing step: {e}")
            return False
    
    def navigate_to_url(self, url: str) -> bool:
        """Navigate to a URL"""
        try:
            if not url:
                logger.error("No URL provided for navigation")
                return False
            
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, Config.SELENIUM_TIMEOUT).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to URL {url}: {e}")
            return False
    
    def find_element(self, element_id: str) -> Optional[Any]:
        """Find element using selector from UI mappings"""
        try:
            selector_info = self.ui_tree_manager.get_element_selector(element_id)
            
            if not selector_info:
                logger.error(f"No selector found for element: {element_id}")
                return None
            
            selector_type = selector_info.get('selector_type', '').lower()
            selector_value = selector_info.get('selector_value', '')
            
            wait = WebDriverWait(self.driver, Config.SELENIUM_TIMEOUT)
            
            if selector_type == 'xpath':
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector_value)))
            elif selector_type == 'id':
                element = wait.until(EC.presence_of_element_located((By.ID, selector_value)))
            elif selector_type == 'name':
                element = wait.until(EC.presence_of_element_located((By.NAME, selector_value)))
            elif selector_type == 'class':
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, selector_value)))
            elif selector_type == 'css':
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_value)))
            else:
                logger.error(f"Unsupported selector type: {selector_type}")
                return None
            
            return element
            
        except TimeoutException:
            logger.error(f"Element not found within timeout: {element_id}")
            return None
        except Exception as e:
            logger.error(f"Error finding element {element_id}: {e}")
            return None
    
    def click_element(self, element_id: str) -> bool:
        """Click an element"""
        try:
            element = self.find_element(element_id)
            if not element:
                return False
            
            # Wait for element to be clickable
            wait = WebDriverWait(self.driver, Config.SELENIUM_TIMEOUT)
            clickable_element = wait.until(EC.element_to_be_clickable(element))
            
            # Scroll to element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", clickable_element)
            time.sleep(0.5)
            
            # Click element
            clickable_element.click()
            logger.info(f"Clicked element: {element_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clicking element {element_id}: {e}")
            return False
    
    def type_text(self, element_id: str, text: str) -> bool:
        """Type text into an element"""
        try:
            if not text:
                logger.warning(f"No text to type for element: {element_id}")
                return True
            
            element = self.find_element(element_id)
            if not element:
                return False
            
            # Clear existing text
            element.clear()
            
            # Type new text
            element.send_keys(text)
            logger.info(f"Typed text into {element_id}: {text}")

            # CUSTOM ADDITION: Press ENTER key after typing
            element.send_keys(Keys.ENTER)
            logger.info(f"Pressed ENTER key after typing into {element_id}")
            # --- END ADDITION ---
            
            return True
            
        except Exception as e:
            logger.error(f"Error typing text into element {element_id}: {e}")
            return False
    
    def get_text_to_type(self, target_element: str, dynamic_values: Dict[str, str], action_value: str) -> str:
        """Determine what text to type based on element and available values"""
        # If action_value is provided, use it
        if action_value:
            return action_value
        
        # Map target elements to dynamic values
        element_mapping = {
            'recipient_field': 'recipient_email',
            'subject_field': 'email_subject',
            'search_box': 'search_query',
            'message_body': 'email_message'
        }
        
        # Get the corresponding dynamic value
        dynamic_key = element_mapping.get(target_element, '')
        if dynamic_key and dynamic_key in dynamic_values:
            return dynamic_values[dynamic_key]
        
        # Default values for common elements
        default_values = {
            'message_body': 'Hello, I hope this message finds you well.',
            'email_subject': 'Inquiry',
            'search_query': 'information'
        }
        
        return default_values.get(target_element, '')
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot of current browser state"""
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(Config.SCREENSHOTS_DIR, filename)
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return ""
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")