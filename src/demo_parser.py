"""
Demo Parser for extracting UI automation steps from demonstration videos
Based on the research paper: https://arxiv.org/abs/2504.13805
"""

import cv2
import numpy as np
from loguru import logger
import json
import os
from pathlib import Path

class DemoParser:
    """
    Parses demonstration videos to extract structured UI automation steps
    This is a simplified implementation based on the referenced paper
    """
    
    def __init__(self):
        self.frame_buffer = []
        self.detected_actions = []
        self.ui_elements = []
        
    def parse_demo_video(self, video_path, output_path=None):
        """
        Parse a demonstration video and extract automation steps
        
        Args:
            video_path: Path to the demonstration video
            output_path: Path to save extracted steps (optional)
            
        Returns:
            List of extracted automation steps
        """
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return []
            
            # Initialize video capture
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return []
            
            logger.info(f"Parsing demo video: {video_path}")
            
            # Extract frames and analyze
            steps = self.extract_steps_from_video(cap)
            
            # Clean up
            cap.release()
            
            # Save steps if output path provided
            if output_path and steps:
                self.save_extracted_steps(steps, output_path)
            
            logger.info(f"Extracted {len(steps)} automation steps from demo")
            return steps
            
        except Exception as e:
            logger.error(f"Error parsing demo video: {e}")
            return []
    
    def extract_steps_from_video(self, cap):
        """Extract automation steps from video frames"""
        steps = []
        frame_count = 0
        prev_frame = None
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Process every nth frame to reduce computation
                if frame_count % 5 == 0:
                    # Detect UI changes and actions
                    if prev_frame is not None:
                        detected_action = self.detect_action_between_frames(prev_frame, frame)
                        if detected_action:
                            steps.append(detected_action)
                    
                    prev_frame = frame.copy()
            
            # Post-process steps to remove duplicates and refine
            refined_steps = self.refine_extracted_steps(steps)
            
            return refined_steps
            
        except Exception as e:
            logger.error(f"Error extracting steps from video: {e}")
            return []
    
    def detect_action_between_frames(self, frame1, frame2):
        """
        Detect UI actions between two consecutive frames
        This is a simplified implementation - real implementation would be more sophisticated
        """
        try:
            # Convert frames to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference
            diff = cv2.absdiff(gray1, gray2)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            
            # Find contours of changed regions
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze significant changes
            significant_changes = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Minimum area threshold
                    x, y, w, h = cv2.boundingRect(contour)
                    significant_changes.append({
                        'x': int(x + w/2),
                        'y': int(y + h/2),
                        'width': w,
                        'height': h,
                        'area': area
                    })
            
            # If significant changes detected, classify the action
            if significant_changes:
                return self.classify_detected_action(significant_changes, frame1, frame2)
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting action between frames: {e}")
            return None
    
    def classify_detected_action(self, changes, frame1, frame2):
        """
        Classify the type of action based on detected changes
        This is a simplified heuristic-based approach
        """
        try:
            # Sort changes by area (largest first)
            changes.sort(key=lambda x: x['area'], reverse=True)
            
            primary_change = changes[0]
            
            # Heuristic classification based on change characteristics
            action_type = "unknown"
            
            # Small, localized changes often indicate clicks
            if primary_change['area'] < 1000 and len(changes) == 1:
                action_type = "click"
            
            # Large changes might indicate navigation or window switching
            elif primary_change['area'] > 10000:
                action_type = "navigate"
            
            # Multiple small changes might indicate typing
            elif len(changes) > 3 and all(c['area'] < 500 for c in changes):
                action_type = "type"
            
            # Medium changes might indicate form interactions
            elif 1000 <= primary_change['area'] <= 10000:
                action_type = "interact"
            
            # Create action step
            step = {
                'action_type': action_type,
                'coordinates': (primary_change['x'], primary_change['y']),
                'region': {
                    'x': primary_change['x'] - primary_change['width']//2,
                    'y': primary_change['y'] - primary_change['height']//2,
                    'width': primary_change['width'],
                    'height': primary_change['height']
                },
                'confidence': self.calculate_confidence(changes),
                'timestamp': len(self.detected_actions)  # Simple timestamp
            }
            
            return step
            
        except Exception as e:
            logger.error(f"Error classifying detected action: {e}")
            return None
    
    def calculate_confidence(self, changes):
        """Calculate confidence score for detected action"""
        try:
            # Simple confidence calculation based on change characteristics
            if not changes:
                return 0.0
            
            primary_change = changes[0]
            confidence = min(1.0, primary_change['area'] / 5000)  # Normalize by area
            
            # Boost confidence if multiple consistent changes
            if len(changes) > 1:
                confidence = min(1.0, confidence * 1.2)
            
            return round(confidence, 2)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.0
    
    def refine_extracted_steps(self, raw_steps):
        """Refine and clean up extracted steps"""
        try:
            if not raw_steps:
                return []
            
            refined_steps = []
            
            # Remove duplicate and very similar steps
            for i, step in enumerate(raw_steps):
                is_duplicate = False
                
                # Check against already refined steps
                for refined_step in refined_steps:
                    if self.are_steps_similar(step, refined_step):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    # Add step order and description
                    step['step_order'] = len(refined_steps) + 1
                    step['description'] = self.generate_step_description(step)
                    refined_steps.append(step)
            
            return refined_steps
            
        except Exception as e:
            logger.error(f"Error refining extracted steps: {e}")
            return raw_steps
    
    def are_steps_similar(self, step1, step2, threshold=50):
        """Check if two steps are similar based on coordinates and action type"""
        try:
            if step1['action_type'] != step2['action_type']:
                return False
            
            # Calculate distance between coordinates
            x1, y1 = step1['coordinates']
            x2, y2 = step2['coordinates']
            distance = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            
            return distance < threshold
            
        except Exception as e:
            logger.error(f"Error comparing steps: {e}")
            return False
    
    def generate_step_description(self, step):
        """Generate human-readable description for a step"""
        try:
            action_type = step['action_type']
            x, y = step['coordinates']
            
            descriptions = {
                'click':