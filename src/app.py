"""
Main Gradio application
"""
import gradio as gr
import threading
import time
from typing import Optional, Any
from src.input_handler import InputHandler
from src.task_processor import TaskProcessor
from src.automation_engine import AutomationEngine
from src.utils.logger import setup_logger
from src.utils.config import Config

logger = setup_logger(__name__, 'app.log')

class TaskAutomationApp:
    def __init__(self):
        self.input_handler = InputHandler()
        self.task_processor = TaskProcessor()
        self.automation_engine = None
        self.current_status = "Ready"
        
        # Ensure directories exist
        Config.ensure_directories()
    
    def process_input(self, text_input: str, voice_input, file_input) -> tuple:
        """Process user input from any modality"""
        try:
            user_input = ""
            
            # Determine input type and process
            if text_input and text_input.strip():
                user_input = self.input_handler.process_text_input(text_input)
                input_type = "text"
            elif voice_input is not None:
                user_input = self.input_handler.process_voice_input(voice_input)
                input_type = "voice"
            elif file_input is not None:
                user_input = self.input_handler.process_file_input(file_input)
                input_type = "file"
            else:
                return "Please provide input through text, voice, or file.", "No input provided", "Ready"
            
            logger.info(f"Processing {input_type} input: {user_input}")
            
            # Process the input to create execution plan
            execution_plan = self.task_processor.process_user_input(user_input)
            
            if not execution_plan:
                return f"Input processed: {user_input}", "Could not understand the task. Please try rephrasing.", "Ready"
            
            # Start automation in a separate thread
            self.start_automation_thread(execution_plan)
            
            task_name = execution_plan['task_info']['task_name']
            return f"Input processed: {user_input}", f"Task identified: {task_name}. Starting automation...", "Processing..."
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return f"Error: {str(e)}", "Failed to process input", "Error"
    
    def start_automation_thread(self, execution_plan: dict):
        """Start automation in a separate thread"""
        def run_automation():
            try:
                # Create automation engine with status callback
                self.automation_engine = AutomationEngine(
                    status_callback=self.update_status
                )
                
                # Execute the task
                success = self.automation_engine.execute_task(execution_plan)
                
                if success:
                    self.current_status = "Task completed successfully!"
                else:
                    self.current_status = "Task failed. Please check the logs."
                    
            except Exception as e:
                logger.error(f"Error in automation thread: {e}")
                self.current_status = f"Error: {str(e)}"
        
        # Start the automation thread
        automation_thread = threading.Thread(target=run_automation, daemon=True)
        automation_thread.start()
    
    def update_status(self, status: str):
        """Update current status"""
        self.current_status = status
    
    def get_current_status(self) -> str:
        """Get current automation status"""
        return self.current_status
    
    def create_interface(self):
        """Create Gradio interface"""
        with gr.Blocks(
            title="AI Task Automation System",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
            }
            .status-box {
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                background-color: #f8f9fa;
            }
            """
        ) as interface:
            
            gr.Markdown(
                """
                # 🤖 AI Task Automation System
                
                This system can automate various tasks based on your input. You can provide instructions through:
                - **Text**: Type your request directly
                - **Voice**: Upload an audio file with your request
                - **File**: Upload a text file with your instructions
                
                **Example tasks:**
                - "Send an email to john@example.com regarding the meeting"
                - "Search Google for Python tutorials"
                - "Navigate to github.com"
                """
            )
            
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### Input Methods")
                    
                    # Text input
                    text_input = gr.Textbox(
                        label="Text Input",
                        placeholder="Enter your task here (e.g., 'Send email to john@example.com about project update')",
                        lines=3
                    )
                    
                    # Voice input
                    voice_input = gr.File(
                        label="Voice Input",
                        file_types=[".wav", ".mp3", ".m4a", ".ogg"],
                        type="binary"
                    )
                    
                    # File input
                    file_input = gr.File(
                        label="File Input",
                        file_types=[".txt"],
                        type="binary"
                    )
                    
                    # Process button
                    process_btn = gr.Button("🚀 Process & Automate", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown("### Automation Status")
                    
                    # Output displays
                    input_display = gr.Textbox(
                        label="Processed Input",
                        interactive=False,
                        lines=2
                    )
                    
                    task_display = gr.Textbox(
                        label="Task Information",
                        interactive=False,
                        lines=2
                    )
                    
                    status_display = gr.Textbox(
                        label="Current Status",
                        interactive=False,
                        lines=3,
                        elem_classes=["status-box"]
                    )
                    
                    # Auto-refresh status every 2 seconds
                    def refresh_status():
                        return self.get_current_status()
                    
                    # Set up automatic status updates
                    status_display.change(
                        fn=refresh_status,
                        outputs=status_display,
                    )
            
            # Example tasks
            gr.Markdown(
                """
                ### 📝 Example Tasks You Can Try:
                
                1. **Email Tasks**: "Compose an email to hello@company.com regarding their services"
                2. **Web Search**: "Search Google for machine learning tutorials"
                3. **Navigation**: "Go to github.com"
                4. **General**: "Open Google and search for weather forecast"
                
                ### 🔧 How It Works:
                
                1. **Input Processing**: Your input is analyzed to identify the task type
                2. **Task Matching**: The system finds the best matching automation template
                3. **Step Execution**: Browser automation executes the required steps
                4. **Status Updates**: Real-time updates show the progress
                
                ### ⚠️ Important Notes:
                
                - The browser will open automatically when processing tasks
                - Tasks involving external websites may require manual intervention
                - Check the status panel for real-time updates
                - Screenshots are saved in the 'screenshots' folder for debugging
                """
            )
            
            # Event handlers
            process_btn.click(
                fn=self.process_input,
                inputs=[text_input, voice_input, file_input],
                outputs=[input_display, task_display, status_display]
            )
            
            # Clear inputs after processing
            def clear_inputs():
                return "", None, None
            
            process_btn.click(
                fn=clear_inputs,
                outputs=[text_input, voice_input, file_input]
            )
        
        return interface
    
    def launch(self):
        """Launch the Gradio application"""
        try:
            interface = self.create_interface()
            
            logger.info("Starting AI Task Automation System...")
            
            interface.launch(
                server_name="127.0.0.1",
                server_port=7860,
                share=False,
                debug=False,
                show_error=True,
                quiet=False
            )
            
        except Exception as e:
            logger.error(f"Error launching application: {e}")
            raise