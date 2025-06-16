"""
Main entry point for the AI Task Automation System
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import TaskAutomationApp

if __name__ == "__main__":
    app = TaskAutomationApp()
    app.launch()