"""
Entry point for the GUI Automation System
Run this file to start the application
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point"""
    try:
        # Create necessary directories
        os.makedirs("data/logs", exist_ok=True)
        
        # Import and run the main application
        from app import create_interface, logger
        
        logger.info("Starting GUI Automation System...")
        
        # Launch the Gradio interface
        interface = create_interface()
        interface.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            debug=False
        )
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()