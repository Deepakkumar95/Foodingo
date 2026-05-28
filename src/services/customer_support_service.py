# src/services/customer_support_service.py
import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)

class CustomerSupportService:
    def __init__(self):
        self.intent_patterns = {
            'order_status': [
                r'status.*order', r'where.*order', r'track.*order',
                r'when.*arrive', r'order.*update'
            ],
            'complaint': [
                r'complaint', r'issue', r'problem', r'wrong', r'missing',
                r'bad', r'poor', r'terrible', r'awful'
            ],
            'menu_inquiry': [
                r'menu', r'what.*serve', r'options', r'vegetarian',
                r'vegan', r'gluten', r'allergy'
            ],
            'delivery_time': [
                r'how long', r'delivery time', r'when.*deliver',
                r'estimated', r'eta'
            ],
            'payment_issue': [
                r'payment', r'charge', r'refund', r'billing',
                r'money', r'cost'
            ]
        }
        
    async def process_customer_query(self, query: Dict) -> Dict:
        """Process multi-modal customer query"""
        response = {'success': True}
        
        # Text processing
        if 'text' in query:
            text_response = await self.process_text_query(query['text'])
            response.update(text_response)
        
        # Audio processing
        if 'audio' in query:
            text_from_speech = await self.speech_to_text(query['audio'])
            voice_response = await self.process_text_query(text_from_speech)
            response.update(voice_response)
            response['original_audio'] = True
        
        # Image processing (would integrate with food recognition)
        if 'image' in query:
            image_analysis = await self.analyze_image(query['image'])
            response['image_analysis'] = image_analysis
        
        return response
    
    async def process_text_query(self, text: str) -> Dict:
        """Process text query with NLP"""
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Classify intent
        intent = await self.classify_intent(cleaned_text)
        
        # Extract entities
        entities = await self.extract_entities(cleaned_text)
        
        # Analyze sentiment
        sentiment = await self.analyze_sentiment(cleaned_text)
        
        # Generate response
        response = await self.generate_response(intent, entities, sentiment, cleaned_text)
        
        return {
            'intent': intent,
            'entities': entities,
            'sentiment': sentiment,
            'response': response,
            'processed_text': cleaned_text
        }
    
    async def classify_intent(self, text: str) -> str:
        """Classify user intent from text"""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        return 'general'
    
    async def extract_entities(self, text: str) -> Dict:
        """Extract entities from text"""
        entities = {
            'order_numbers': re.findall(r'order[#\s]*([A-Z0-9]+)', text, re.IGNORECASE),
            'dates': re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text),
            'times': re.findall(r'\d{1,2}:\d{2}\s*(?:AM|PM)?', text, re.IGNORECASE),
            'amounts': re.findall(r'\$\d+(?:\.\d{2})?', text)
        }
        
        # Clean empty lists
        return {k: v for k, v in entities.items() if v}
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'thanks', 'thank']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'angry', 'frustrated', 'disappointed']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = min(positive_count / 10, 1.0)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = min(negative_count / 10, 1.0)
        else:
            sentiment = 'neutral'
            score = 0.5
        
        return {'sentiment': sentiment, 'score': score}
    
    async def generate_response(self, intent: str, entities: Dict, sentiment: Dict, 
                              original_text: str) -> str:
        """Generate appropriate response based on intent and context"""
        if intent == 'order_status':
            return await self.handle_order_status(entities)
        elif intent == 'complaint':
            return await self.handle_complaint(sentiment, entities)
        elif intent == 'menu_inquiry':
            return await self.handle_menu_inquiry(entities)
        elif intent == 'delivery_time':
            return await self.handle_delivery_time(entities)
        elif intent == 'payment_issue':
            return await self.handle_payment_issue(entities)
        else:
            return await self.handle_general_query(original_text)
    
    async def handle_order_status(self, entities: Dict) -> str:
        """Handle order status inquiries"""
        order_numbers = entities.get('order_numbers', [])
        
        if order_numbers:
            order_num = order_numbers[0]
            return f"I'll check the status of order {order_num} for you right away. It looks like your order is being prepared and should be delivered within 30 minutes."
        else:
            return "I'd be happy to check your order status! Could you please provide your order number?"
    
    async def handle_complaint(self, sentiment: Dict, entities: Dict) -> str:
        """Handle customer complaints"""
        if sentiment['sentiment'] == 'negative':
            apology = "I'm really sorry to hear about your experience. "
        else:
            apology = "I'm sorry to hear that. "
        
        return apology + "Let me help resolve this issue for you. Could you please provide more details about what went wrong?"
    
    async def handle_menu_inquiry(self, entities: Dict) -> str:
        """Handle menu-related inquiries"""
        return "I can help you with menu information! We have a wide variety of options including vegetarian, vegan, and gluten-free choices. Is there a specific cuisine or dietary requirement you're looking for?"
    
    async def handle_delivery_time(self, entities: Dict) -> str:
        """Handle delivery time inquiries"""
        return "Delivery times typically range from 25-45 minutes depending on your location and restaurant preparation time. I can check the exact estimated delivery time for your area if you'd like!"
    
    async def handle_payment_issue(self, entities: Dict) -> str:
        """Handle payment-related issues"""
        amounts = entities.get('amounts', [])
        if amounts:
            return f"I see there's an issue with the amount {amounts[0]}. Let me look into this and help resolve the payment problem."
        else:
            return "I can help with payment issues. Could you please specify what problem you're experiencing with your payment?"
    
    async def handle_general_query(self, text: str) -> str:
        """Handle general queries"""
        return "Thanks for reaching out! I'm here to help with your food delivery needs. How can I assist you today?"
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text"""
        # In production, this would use speech recognition API
        logger.info("Processing audio data...")
        return "What is the status of my order?"
    
    async def analyze_image(self, image_data: bytes) -> Dict:
        """Analyze image content"""
        # In production, this would use computer vision API
        logger.info("Processing image data...")
        return {
            'analysis': 'food_image',
            'confidence': 0.85,
            'items_detected': ['pizza', 'salad']
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\?\!]', '', text)
        
        return text.strip()
