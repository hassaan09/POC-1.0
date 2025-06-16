#!/usr/bin/env python3
"""
Main entry point for GUI Automation System
Launches the Gradio web interface
"""

import sys
import os
from pathlib import Path
from loguru import logger

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def setup_logging():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    logs_dir = Path("data/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure loguru
    logger.remove()  # Remove default handler
    logger.add(
        "data/logs/app_{time}.log",
        rotation="10 MB",
        retention="10 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    )

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        'gradio',
        'pandas',
        'pyautogui',
        'selenium',
        'speech_recognition',
        'sklearn',
        'cv2',
        'loguru'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'cv2':
                import cv2
            elif module == 'sklearn':
                import sklearn
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Missing required modules: {', '.join(missing_modules)}")
        logger.error("Please install missing modules using: pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """Create necessary directories for the application"""
    directories = [
        "data",
        "data/logs",
        "data/screenshots",
        "data/demos",
        "data/extracted_steps"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting GUI Automation System")
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Create necessary directories
        create_directories()
        
        # Import and launch the application
        from src.app import create_interface
        
        logger.info("Initializing Gradio interface...")
        interface = create_interface()
        
        # Launch the interface
        logger.info("Launching GUI Automation System...")
        interface.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7860,       # Default Gradio port
            share=False,            # Set to True to create public link
            debug=False,            # Set to True for debugging
            show_error=True,        # Show detailed errors
            quiet=False             # Show startup messages
        )
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()