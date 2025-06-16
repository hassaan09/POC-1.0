"""
Main Gradio application for GUI Automation System
Handles multi-modal inputs and coordinates automation tasks
"""

import gradio as gr
import pandas as pd
from loguru import logger
import asyncio
from threading import Thread
import time

from input_processor import InputProcessor
from automation_engine import AutomationEngine
from ui_tree import UITreeManager
from tfidf_matcher import TFIDFMatcher

# Configure logger
logger.add("data/logs/app_{time}.log", rotation="10 MB", level="INFO")

class AutomationSystem:
    """Main system class that coordinates all components"""
    
    def __init__(self):
        self.input_processor = InputProcessor()
        self.ui_tree_manager = UITreeManager()
        self.tfidf_matcher = TFIDFMatcher()
        self.automation_engine = AutomationEngine()
        self.current_task_log = []
        
    def process_input(self, text_input, voice_input, file_input):
        """Process multi-modal input and trigger automation"""
        try:
            # Clear previous task log
            self.current_task_log.clear()
            
            # Process inputs
            processed_text = self.input_processor.process_inputs(
                text_input, voice_input, file_input
            )
            
            if not processed_text:
                return "No valid input provided", "No automation steps"
            
            self.current_task_log.append(f"Input processed: {processed_text}")
            logger.info(f"Processing input: {processed_text}")
            
            # Find matching actions using TF-IDF
            matched_actions = self.tfidf_matcher.find_best_match(processed_text)
            
            if not matched_actions:
                return "No matching actions found", "Please add more UI mappings"
            
            self.current_task_log.append(f"Found matching actions: {len(matched_actions)}")
            
            # Get UI steps from tree
            ui_steps = self.ui_tree_manager.get_automation_steps(matched_actions[0])
            
            if not ui_steps:
                return "No automation steps found", "UI Tree mapping incomplete"
            
            # Execute automation
            self.execute_automation_async(ui_steps)
            
            return f"Task initiated: {processed_text}", self.format_log()
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return f"Error: {str(e)}", "Automation failed"
    
    def execute_automation_async(self, steps):
        """Execute automation in a separate thread"""
        def run_automation():
            for step in steps:
                try:
                    self.current_task_log.append(f"Executing: {step['action']}")
                    result = self.automation_engine.execute_step(step)
                    self.current_task_log.append(f"Completed: {step['action']}")
                    time.sleep(1)  # Pause between steps
                except Exception as e:
                    self.current_task_log.append(f"Error in step: {e}")
                    logger.error(f"Automation step failed: {e}")
        
        thread = Thread(target=run_automation)
        thread.daemon = True
        thread.start()
    
    def format_log(self):
        """Format current task log for display"""
        return "\n".join(self.current_task_log) if self.current_task_log else "No steps executed yet"
    
    def get_live_log(self):
        """Get current automation log for live updates"""
        return self.format_log()

# Initialize system
automation_system = AutomationSystem()

def create_interface():
    """Create and configure Gradio interface"""
    
    with gr.Blocks(title="GUI Automation System", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("# 🤖 GUI Automation System")
        gr.Markdown("Enter your task using voice, text, or file input. The system will automate the GUI actions for you.")
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### Input Methods")
                
                # Text input
                text_input = gr.Textbox(
                    label="Text Input",
                    placeholder="e.g., Make an email to hello@shiza.ai regarding their product",
                    lines=3
                )
                
                # Voice input
                voice_input = gr.Audio(
                    sources="microphone",
                    label="Voice Input",
                    type="filepath"
                )
                
                # File input
                file_input = gr.File(
                    label="File Input",
                    file_types=[".txt", ".pdf", ".docx"]
                )
                
                # Submit button
                submit_btn = gr.Button("🚀 Start Automation", variant="primary", size="lg")
                
            with gr.Column(scale=2):
                gr.Markdown("### Automation Status")
                
                # Task status
                task_status = gr.Textbox(
                    label="Current Task",
                    interactive=False,
                    lines=2
                )
                
                # Live automation log
                automation_log = gr.Textbox(
                    label="Automation Steps",
                    interactive=False,
                    lines=10,
                    max_lines=15
                )
                
                # Refresh log button
                refresh_btn = gr.Button("🔄 Refresh Log", size="sm")
        
        with gr.Row():
            gr.Markdown("### System Information")
            
            with gr.Column():
                gr.Markdown("""
                **Supported Actions:**
                - Email composition and sending
                - Web browsing and navigation
                - File operations
                - Application launching
                - Data entry tasks
                
                **Input Formats:**
                - Natural language text
                - Voice commands (English)
                - Text files with instructions
                """)
        
        # Event handlers
        submit_btn.click(
            fn=automation_system.process_input,
            inputs=[text_input, voice_input, file_input],
            outputs=[task_status, automation_log]
        )
        
        refresh_btn.click(
            fn=automation_system.get_live_log,
            outputs=automation_log
        )
        
        # Auto-refresh log every 2 seconds
        interface.load(
            fn=automation_system.get_live_log,
            outputs=automation_log,
        )
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True)