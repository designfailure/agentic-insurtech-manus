"""
Sentiment analyzer tool for the Customer Assistant agent.
"""
from app.agents.tools.mock_crewai import BaseTool
import json
import re
from collections import Counter

class SentimentAnalyzerTool:
    """
    Tool for analyzing customer sentiment in messages and feedback.
    """
    def __init__(self):
        """
        Initialize the sentiment analyzer tool.
        """
        # Sentiment lexicons (simplified)
        self.positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "helpful", "satisfied", "happy", "pleased", "love", "like", "best",
            "thank", "thanks", "appreciate", "outstanding", "perfect", "awesome",
            "easy", "clear", "fast", "quick", "responsive", "friendly", "efficient"
        ]
        
        self.negative_words = [
            "bad", "poor", "terrible", "awful", "horrible", "disappointing",
            "frustrated", "unhappy", "dissatisfied", "angry", "upset", "hate",
            "dislike", "worst", "slow", "difficult", "confusing", "complicated",
            "expensive", "overpriced", "rude", "unprofessional", "inefficient",
            "problem", "issue", "complaint", "error", "mistake", "delay", "fail"
        ]
        
        self.neutral_words = [
            "okay", "ok", "fine", "average", "neutral", "fair", "decent",
            "acceptable", "moderate", "standard", "normal", "regular", "usual"
        ]
        
        # Emotion categories
        self.emotion_words = {
            "anger": ["angry", "furious", "outraged", "mad", "irritated", "annoyed"],
            "frustration": ["frustrated", "stuck", "difficult", "confusing", "complicated"],
            "satisfaction": ["satisfied", "pleased", "content", "happy", "glad"],
            "confusion": ["confused", "unclear", "unsure", "uncertain", "puzzled"],
            "urgency": ["urgent", "immediately", "asap", "emergency", "quickly", "soon"]
        }
        
        # Intensity modifiers
        self.intensity_modifiers = {
            "very": 1.5,
            "extremely": 2.0,
            "really": 1.5,
            "somewhat": 0.5,
            "slightly": 0.3,
            "a bit": 0.3,
            "absolutely": 2.0,
            "completely": 1.8,
            "totally": 1.8
        }
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment in text.
        
        Args:
            text: The text to analyze.
            
        Returns:
            Dictionary containing sentiment analysis results.
        """
        # Preprocess text
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        
        # Count sentiment words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        neutral_count = sum(1 for word in words if word in self.neutral_words)
        
        # Calculate base sentiment score (-1 to 1)
        total_sentiment_words = positive_count + negative_count + neutral_count
        if total_sentiment_words == 0:
            sentiment_score = 0  # Neutral if no sentiment words
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
        
        # Adjust for intensity modifiers
        for modifier, multiplier in self.intensity_modifiers.items():
            if modifier in text:
                # Find words that follow the modifier
                modifier_pattern = rf"{modifier}\s+(\w+)"
                matches = re.findall(modifier_pattern, text)
                
                for match in matches:
                    if match in self.positive_words:
                        sentiment_score += (multiplier - 1) * (1 / total_sentiment_words if total_sentiment_words > 0 else 0.1)
                    elif match in self.negative_words:
                        sentiment_score -= (multiplier - 1) * (1 / total_sentiment_words if total_sentiment_words > 0 else 0.1)
        
        # Ensure score is within -1 to 1 range
        sentiment_score = max(-1, min(1, sentiment_score))
        
        # Determine sentiment category
        if sentiment_score > 0.3:
            sentiment = "positive"
        elif sentiment_score < -0.3:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Detect emotions
        emotions = {}
        for emotion, emotion_words in self.emotion_words.items():
            emotion_count = sum(1 for word in words if word in emotion_words)
            if emotion_count > 0:
                emotions[emotion] = emotion_count
        
        # Get top emotions
        top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(text)
        
        return {
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "emotions": dict(top_emotions) if top_emotions else {},
            "key_phrases": key_phrases
        }
    
    def _extract_key_phrases(self, text):
        """
        Extract key phrases from text.
        
        Args:
            text: The text to analyze.
            
        Returns:
            List of key phrases.
        """
        # Simple key phrase extraction based on sentiment words
        phrases = []
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            words = re.findall(r'\b\w+\b', sentence.lower())
            
            # Check if sentence contains sentiment words
            has_sentiment = any(word in self.positive_words or word in self.negative_words for word in words)
            
            if has_sentiment and 3 <= len(words) <= 15:
                phrases.append(sentence)
        
        return phrases[:3]  # Return top 3 phrases
    
    def get_tool(self):
        """
        Get the CrewAI tool for sentiment analysis.
        
        Returns:
            CrewAI BaseTool instance.
        """
        return BaseTool(
            name="sentiment_analysis_tool",
            description="Analyzes sentiment in customer messages and feedback",
            func=self._sentiment_analysis_tool
        )
    
    def _sentiment_analysis_tool(self, text):
        """
        Tool function for sentiment analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            JSON string of sentiment analysis results.
        """
        try:
            results = self.analyze_sentiment(text)
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
