"""
Input processor for handling voice, text, and file inputs
Converts all inputs to standardized text format
"""

import speech_recognition as sr
import os
from pathlib import Path
from loguru import logger
import pandas as pd

class InputProcessor:
    """Processes different types of user inputs"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Initialize speech recognition
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
        except Exception as e:
            logger.warning(f"Microphone not available: {e}")
    
    def process_inputs(self, text_input, voice_input, file_input):
        """
        Process all input types and return unified text
        Priority: Text > Voice > File
        """
        processed_text = ""
        
        # Process text input (highest priority)
        if text_input and text_input.strip():
            processed_text = text_input.strip()
            logger.info("Using text input")
            return processed_text
        
        # Process voice input
        if voice_input:
            voice_text = self.process_voice_input(voice_input)
            if voice_text:
                processed_text = voice_text
                logger.info("Using voice input")
                return processed_text
        
        # Process file input (lowest priority)
        if file_input:
            file_text = self.process_file_input(file_input)
            if file_text:
                processed_text = file_text
                logger.info("Using file input")
                return processed_text
        
        return processed_text
    
    def process_voice_input(self, audio_file_path):
        """Convert voice input to text using speech recognition"""
        try:
            if not audio_file_path or not os.path.exists(audio_file_path):
                return ""
            
            # Use speech recognition to convert audio to text
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Voice input recognized: {text}")
                return text
                
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return ""
    
    def process_file_input(self, file_path):
        """Extract text from uploaded files"""
        try:
            if not file_path or not os.path.exists(file_path):
                return ""
            
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.txt':
                return self.read_text_file(file_path)
            elif file_extension == '.pdf':
                return self.read_pdf_file(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self.read_docx_file(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return ""
                
        except Exception as e:
            logger.error(f"Error processing file input: {e}")
            return ""
    
    def read_text_file(self, file_path):
        """Read content from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                logger.info(f"Read text file: {len(content)} characters")
                return content
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            return ""
    
    def read_pdf_file(self, file_path):
        """Read content from PDF file"""
        try:
            # Try to import PyPDF2 for PDF reading
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                logger.info(f"Read PDF file: {len(text)} characters")
                return text.strip()
                
        except ImportError:
            logger.warning("PyPDF2 not installed, cannot read PDF files")
            return ""
        except Exception as e:
            logger.error(f"Error reading PDF file: {e}")
            return ""
    
    def read_docx_file(self, file_path):
        """Read content from DOCX file"""
        try:
            # Try to import python-docx for DOCX reading
            from docx import Document
            
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            logger.info(f"Read DOCX file: {len(text)} characters")
            return text.strip()
            
        except ImportError:
            logger.warning("python-docx not installed, cannot read DOCX files")
            return ""
        except Exception as e:
            logger.error(f"Error reading DOCX file: {e}")
            return ""
    
    def preprocess_text(self, text):
        """Clean and preprocess text for better matching"""
        if not text:
            return ""
        
        # Basic text cleaning
        text = text.strip()
        text = ' '.join(text.split())  # Remove extra whitespace
        
        # Convert to lowercase for processing
        processed_text = text.lower()
        
        logger.debug(f"Preprocessed text: {processed_text}")
        return processed_text