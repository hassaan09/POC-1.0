"""
Handles different types of input (text, voice, file)
"""
import speech_recognition as sr
import tempfile
import os
from typing import Optional, Tuple
from src.utils.logger import setup_logger

logger = setup_logger(__name__, 'input_handler.log')

class InputHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
    def process_text_input(self, text: str) -> str:
        """Process text input"""
        if not text or not text.strip():
            raise ValueError("Text input cannot be empty")
        return text.strip()
    
    def process_voice_input(self, audio_file) -> str:
        """Process voice input from uploaded audio file"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_file)
                tmp_file_path = tmp_file.name
            
            # Process audio file
            with sr.AudioFile(tmp_file_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            logger.info(f"Voice input transcribed: {text}")
            return text
            
        except sr.UnknownValueError:
            raise ValueError("Could not understand audio")
        except sr.RequestError as e:
            raise ValueError(f"Speech recognition error: {e}")
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            raise ValueError(f"Error processing voice input: {e}")
    
    def process_file_input(self, file) -> str:
        """Process text file input"""
        try:
            if file is None:
                raise ValueError("No file provided")
            
            # Read file content
            content = file.decode('utf-8')
            
            if not content.strip():
                raise ValueError("File is empty")
                
            logger.info(f"File input processed, length: {len(content)}")
            return content.strip()
            
        except UnicodeDecodeError:
            raise ValueError("File must be a text file (UTF-8 encoded)")
        except Exception as e:
            logger.error(f"Error processing file input: {e}")
            raise ValueError(f"Error processing file: {e}")
