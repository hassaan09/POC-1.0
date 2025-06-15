"""
TF-IDF Matcher for finding best matching actions based on user input
Uses scikit-learn's TfidfVectorizer for intelligent action matching
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from loguru import logger
import re
from ui_tree import UITreeManager

class TFIDFMatcher:
    """Matches user input to automation actions using TF-IDF similarity"""
    
    def __init__(self):
        self.ui_tree_manager = UITreeManager()
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        self.action_vectors = None
        self.action_texts = []
        self.action_ids = []
        self.build_action_corpus()
    
    def build_action_corpus(self):
        """Build corpus of action descriptions for TF-IDF matching"""
        try:
            actions = self.ui_tree_manager.get_all_actions()
            
            self.action_texts = []
            self.action_ids = []
            
            for action in actions:
                # Combine action name and keywords for better matching
                action_text = f"{action['action_name']} {' '.join(action['keywords'])}"
                self.action_texts.append(action_text)
                self.action_ids.append(action['action_id'])
            
            # Fit TF-IDF vectorizer on action corpus
            if self.action_texts:
                self.action_vectors = self.vectorizer.fit_transform(self.action_texts)
                logger.info(f"Built TF-IDF corpus with {len(self.action_texts)} actions")
            else:
                logger.warning("No actions available for TF-IDF matching")
                
        except Exception as e:
            logger.error(f"Error building action corpus: {e}")
    
    def find_best_match(self, user_input, top_k=3, threshold=0.1):
        """
        Find best matching actions for user input
        Returns list of action IDs sorted by similarity score
        """
        try:
            if not user_input or not self.action_vectors:
                return []
            
            # Preprocess user input
            processed_input = self.preprocess_input(user_input)
            
            # Transform user input to TF-IDF vector
            input_vector = self.vectorizer.transform([processed_input])
            
            # Calculate cosine similarity with all actions
            similarities = cosine_similarity(input_vector, self.action_vectors).flatten()
            
            # Get top-k matches above threshold
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            matches = []
            for idx in top_indices:
                if similarities[idx] >= threshold:
                    matches.append({
                        'action_id': self.action_ids[idx],
                        'similarity': float(similarities[idx]),
                        'action_text': self.action_texts[idx]
                    })
            
            logger.info(f"Found {len(matches)} matches for input: {user_input}")
            
            # Return just action IDs for now
            return [match['action_id'] for match in matches]
            
        except Exception as e:
            logger.error(f"Error finding best match: {e}")
            return []
    
    def preprocess_input(self, text):
        """Preprocess user input for better matching"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Expand common abbreviations and synonyms
        text = self.expand_synonyms(text)
        
        return text
    
    def expand_synonyms(self, text):
        """Expand synonyms and abbreviations for better matching"""
        synonyms = {
            'mail': 'email',
            'e-mail': 'email',
            'message': 'email',
            'letter': 'email',
            'browse': 'open website',
            'surf': 'open website',
            'navigate': 'open website',
            'visit': 'open website',
            'go to': 'open website',
            'launch': 'open',
            'start': 'open',
            'run': 'open',
            'execute': 'open',
            'write': 'type',
            'enter': 'type',
            'input': 'type',
            'fill': 'type',
            'press': 'click',
            'hit': 'click',
            'tap': 'click',
            'select': 'click'
        }
        
        for synonym, replacement in synonyms.items():
            text = text.replace(synonym, replacement)
        
        return text
    
    def get_similarity_score(self, user_input, action_id):
        """Get similarity score between user input and specific action"""
        try:
            if action_id not in self.action_ids:
                return 0.0
            
            action_index = self.action_ids.index(action_id)
            processed_input = self.preprocess_input(user_input)
            input_vector = self.vectorizer.transform([processed_input])
            
            action_vector = self.action_vectors[action_index:action_index+1]
            similarity = cosine_similarity(input_vector, action_vector)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity score: {e}")
            return 0.0
    
    def update_corpus(self):
        """Update TF-IDF corpus when new actions are added"""
        try:
            self.build_action_corpus()
            logger.info("TF-IDF corpus updated")
            
        except Exception as e:
            logger.error(f"Error updating corpus: {e}")
    
    def get_action_suggestions(self, partial_input, max_suggestions=5):
        """Get action suggestions based on partial user input"""
        try:
            if not partial_input or len(partial_input) < 2:
                return []
            
            matches = self.find_best_match(partial_input, top_k=max_suggestions, threshold=0.05)
            
            suggestions = []
            for action_id in matches:
                action_name = self.ui_tree_manager.ui_mappings.get(action_id, {}).get('action_name', action_id)
                suggestions.append({
                    'action_id': action_id,
                    'action_name': action_name,
                    'score': self.get_similarity_score(partial_input, action_id)
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting action suggestions: {e}")
            return []
    
    def analyze_input_intent(self, user_input):
        """Analyze user input to extract intent and parameters"""
        try:
            # Basic intent analysis - can be expanded with NLP libraries
            analysis = {
                'intent': 'unknown',
                'entities': {},
                'confidence': 0.0
            }
            
            # Email intent patterns
            email_patterns = [
                r'email.*to\s+([^\s@]+@[^\s@]+\.[^\s@]+)',
                r'send.*([^\s@]+@[^\s@]+\.[^\s@]+)',
                r'compose.*email',
                r'write.*email'
            ]
            
            # Web intent patterns
            web_patterns = [
                r'open\s+(https?://[^\s]+)',
                r'go\s+to\s+(https?://[^\s]+)',
                r'browse\s+(https?://[^\s]+)',
                r'visit\s+([^\s]+\.[^\s]+)'
            ]
            
            text_lower = user_input.lower()
            
            # Check for email intent
            for pattern in email_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    analysis['intent'] = 'email'
                    if match.groups():
                        analysis['entities']['email'] = match.group(1)
                    analysis['confidence'] = 0.8
                    break
            
            # Check for web intent
            if analysis['intent'] == 'unknown':
                for pattern in web_patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        analysis['intent'] = 'web_browse'
                        if match.groups():
                            analysis['entities']['url'] = match.group(1)
                        analysis['confidence'] = 0.8
                        break
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing input intent: {e}")
            return {'intent': 'unknown', 'entities': {}, 'confidence': 0.0}