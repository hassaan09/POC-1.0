"""
Configuration settings for the application
"""
import os

class Config:
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    SCREENSHOTS_DIR = os.path.join(BASE_DIR, 'screenshots')
    
    # Files
    UI_MAPPINGS_FILE = os.path.join(DATA_DIR, 'ui_mappings.xlsx')
    
    # Selenium settings
    SELENIUM_TIMEOUT = 10
    IMPLICIT_WAIT = 5
    
    # TFIDF settings
    TFIDF_MIN_SIMILARITY = 0.1
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.DATA_DIR, cls.LOGS_DIR, cls.SCREENSHOTS_DIR]:
            os.makedirs(directory, exist_ok=True)
