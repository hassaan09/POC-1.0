"""
Automation Engine for executing GUI automation tasks
Handles various types of automation actions like clicking, typing, web navigation
"""

import pyautogui
import time
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
import cv2
import numpy as np

# Configure PyAutoGUI safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

class AutomationEngine:
    """Executes GUI automation steps"""
    
    def __init__(self):
        self.driver = None
        self.current_window = None
        self.setup_selenium()
    
    def setup_selenium(self):
        """Setup Selenium WebDriver for web automation"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--start-maximized")
            
            # Initialize Chrome driver
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up Selenium: {e}")
            self.driver = None
    
    def execute_step(self, step):
        """Execute a single automation step"""
        try:
            action_type = step.get('action', '').lower()
            selector = step.get('selector', '')
            parameters = step.get('parameters', {})
            
            logger.info(f"Executing step: {step.get('description', 'Unknown')}")
            
            if action_type == 'web_navigate':
                return self.web_navigate(selector, parameters)
            elif action_type == 'click':
                return self.click_element(selector, parameters)
            elif action_type == 'type':
                return self.type_text(selector, parameters)
            elif action_type == 'form_fill':
                return self.fill_form(selector, parameters)
            elif action_type == 'app_launch':
                return self.launch_application(selector, parameters)
            elif action_type == 'file_open':
                return self.open_file(selector, parameters)
            elif action_type == 'wait':
                return self.wait_for_element(selector, parameters)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing step: {e}")
            return False
    
    def web_navigate(self, url, parameters=None):
        """Navigate to a web URL"""
        try:
            if not self.driver:
                logger.error("WebDriver not available")
                return False
            
            # Handle URL parameter substitution
            if parameters and 'url' in parameters:
                url = parameters['url']
            
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            self.driver.get(url)
            logger.info(f"Navigated to: {url}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to URL: {e}")
            return False
    
    def click_element(self, selector, parameters=None):
        """Click on an element using CSS selector or coordinates"""
        try:
            if self.driver and selector.startswith(('div', 'button', 'a', 'input', '.')):
                # Web element click using Selenium
                return self.click_web_element(selector, parameters)
            else:
                # Desktop element click using PyAutoGUI
                return self.click_desktop_element(selector, parameters)
                
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return False
    
    def click_web_element(self, selector, parameters=None):
        """Click web element using Selenium"""
        try:
            if not self.driver:
                return False
            
            # Wait for element to be clickable
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            # Click the element
            element.click()
            logger.info(f"Clicked web element: {selector}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clicking web element: {e}")
            return False
    
    def click_desktop_element(self, selector, parameters=None):
        """Click desktop element using PyAutoGUI"""
        try:
            # If selector contains coordinates
            if ',' in selector:
                coords = selector.split(',')
                x, y = int(coords[0]), int(coords[1])
                pyautogui.click(x, y)
                logger.info(f"Clicked at coordinates: ({x}, {y})")
                return True
            
            # Try to find element by image or text
            return self.find_and_click_by_image(selector, parameters)
            
        except Exception as e:
            logger.error(f"Error clicking desktop element: {e}")
            return False
    
    def find_and_click_by_image(self, image_path, parameters=None):
        """Find and click element by image recognition"""
        try:
            # This is a placeholder for image recognition
            # In a full implementation, you would use OpenCV or similar
            # to find UI elements by screenshot comparison
            
            logger.warning("Image-based clicking not fully implemented")
            return False
            
        except Exception as e:
            logger.error(f"Error in image-based clicking: {e}")
            return False
    
    def type_text(self, selector, parameters=None):
        """Type text into an input field"""
        try:
            text_to_type = parameters.get('text', '') if parameters else ''
            
            if self.driver and selector.startswith(('input', 'textarea', '.')):
                # Web input using Selenium
                return self.type_web_text(selector, text_to_type)
            else:
                # Desktop input using PyAutoGUI
                return self.type_desktop_text(text_to_type)
                
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False
    
    def type_web_text(self, selector, text):
        """Type text in web input field"""
        try:
            if not self.driver:
                return False
            
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # Clear existing text and type new text
            element.clear()
            element.send_keys(text)
            logger.info(f"Typed text in web element: {selector}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error typing in web element: {e}")
            return False
    
    def type_desktop_text(self, text):
        """Type text using PyAutoGUI"""
        try:
            pyautogui.typewrite(text, interval=0.05)
            logger.info(f"Typed text: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Error typing desktop text: {e}")
            return False
    
    def fill_form(self, selector, parameters=None):
        """Fill out a form with multiple fields"""
        try:
            if not parameters:
                return False
            
            # Handle email form filling
            if 'recipient' in parameters:
                return self.fill_email_form(parameters)
            
            # Handle other form types
            return self.fill_generic_form(selector, parameters)
            
        except Exception as e:
            logger.error(f"Error filling form: {e}")
            return False
    
    def fill_email_form(self, parameters):
        """Fill Gmail compose form"""
        try:
            if not self.driver:
                return False
            
            # Wait for compose window to load
            time.sleep(2)
            
            # Fill recipient
            if 'recipient' in parameters:
                recipient_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[peoplekit-id="To"]'))
                )
                recipient_field.send_keys(parameters['recipient'])
            
            # Fill subject
            if 'subject' in parameters:
                subject_field = self.driver.find_element(By.CSS_SELECTOR, 'input[name="subjectbox"]')
                subject_field.send_keys(parameters['subject'])
            
            # Fill body
            if 'body' in parameters:
                body_field = self.driver.find_element(By.CSS_SELECTOR, 'div[role="textbox"]')
                body_field.send_keys(parameters['body'])
            
            logger.info("Email form filled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error filling email form: {e}")
            return False
    
    def fill_generic_form(self, selector, parameters):
        """Fill generic form fields"""
        try:
            # Implementation for generic form filling
            logger.info("Generic form filling not fully implemented")
            return True
            
        except Exception as e:
            logger.error(f"Error filling generic form: {e}")
            return False
    
    def launch_application(self, app_path, parameters=None):
        """Launch a desktop application"""
        try:
            if app_path.lower() == 'explorer.exe':
                subprocess.Popen('explorer.exe')
            else:
                subprocess.Popen(app_path)
            
            logger.info(f"Launched application: {app_path}")
            time.sleep(2)  # Wait for app to start
            return True
            
        except Exception as e:
            logger.error(f"Error launching application: {e}")
            return False
    
    def open_file(self, file_path, parameters=None):
        """Open a file with default application"""
        try:
            if parameters and 'filename' in parameters:
                file_path = parameters['filename']
            
            os.startfile(file_path)
            logger.info(f"Opened file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return False
    
    def wait_for_element(self, selector, parameters=None):
        """Wait for an element to appear"""
        try:
            wait_time = parameters.get('timeout', 5) if parameters else 5
            
            if self.driver and selector.startswith(('div', 'button', 'input', '.')):
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            else:
                time.sleep(wait_time)
            
            logger.info(f"Waited for element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Error waiting for element: {e}")
            return False
    
    def take_screenshot(self, filename=None):
        """Take a screenshot for debugging"""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            logger.info(f"Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()