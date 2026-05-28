# src/services/food_recognition_service.py
import logging
from typing import Dict, List, Optional
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

class FoodRecognitionService:
    def __init__(self):
        self.food_categories = {
            'pizza': {'calories': 285, 'carbs': 36, 'protein': 12, 'fat': 10},
            'burger': {'calories': 354, 'carbs': 35, 'protein': 17, 'fat': 16},
            'pasta': {'calories': 221, 'carbs': 43, 'protein': 8, 'fat': 1},
            'salad': {'calories': 35, 'carbs': 7, 'protein': 1, 'fat': 0},
            'sushi': {'calories': 150, 'carbs': 28, 'protein': 6, 'fat': 2},
            'ice_cream': {'calories': 207, 'carbs': 24, 'protein': 3, 'fat': 11}
        }
        
    async def analyze_food_image(self, image_data: bytes) -> Dict:
        """Analyze food image for recognition and nutrition"""
        try:
            # Load and preprocess image
            image = Image.open(io.BytesIO(image_data))
            processed_image = await self.preprocess_image(image)
            
            # Detect food items (simplified - in production would use ML model)
            detected_items = await self.detect_food_items(processed_image)
            
            # Estimate nutrition
            nutrition_info = await self.estimate_nutrition(detected_items)
            
            # Assess quality and freshness
            quality_assessment = await self.assess_quality(processed_image, detected_items)
            
            logger.info(f"Analyzed food image: {len(detected_items)} items detected")
            
            return {
                'success': True,
                'detected_items': detected_items,
                'nutrition_info': nutrition_info,
                'quality_assessment': quality_assessment,
                'confidence': self.calculate_confidence(detected_items)
            }
            
        except Exception as e:
            logger.error(f"Food image analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'detected_items': [],
                'nutrition_info': {},
                'quality_assessment': {}
            }
    
    async def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for analysis"""
        # Resize to standard size
        image = image.resize((224, 224))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    async def detect_food_items(self, image: Image.Image) -> List[Dict]:
        """Detect food items in image"""
        # In production, this would use a trained ML model
        # For demo purposes, return mock detections
        
        # Simulate ML model inference
        mock_detections = [
            {
                'item': 'pizza',
                'confidence': 0.92,
                'bounding_box': [0.1, 0.1, 0.8, 0.8],
                'portion_size': 'large'
            },
            {
                'item': 'salad',
                'confidence': 0.87,
                'bounding_box': [0.6, 0.6, 0.9, 0.9],
                'portion_size': 'side'
            }
        ]
        
        return mock_detections
    
    async def estimate_nutrition(self, detected_items: List[Dict]) -> Dict:
        """Estimate nutrition information for detected food items"""
        total_calories = 0
        total_carbs = 0
        total_protein = 0
        total_fat = 0
        
        for item in detected_items:
            food_type = item['item']
            portion_size = item.get('portion_size', 'medium')
            
            if food_type in self.food_categories:
                nutrition = self.food_categories[food_type]
                portion_multiplier = self.get_portion_multiplier(portion_size)
                
                total_calories += nutrition['calories'] * portion_multiplier
                total_carbs += nutrition['carbs'] * portion_multiplier
                total_protein += nutrition['protein'] * portion_multiplier
                total_fat += nutrition['fat'] * portion_multiplier
        
        return {
            'total_calories': round(total_calories),
            'total_carbs': round(total_carbs),
            'total_protein': round(total_protein),
            'total_fat': round(total_fat),
            'breakdown': [
                {
                    'item': item['item'],
                    'calories': round(self.food_categories.get(item['item'], {}).get('calories', 0) * 
                                    self.get_portion_multiplier(item.get('portion_size', 'medium'))),
                    'portion_size': item.get('portion_size', 'medium')
                }
                for item in detected_items
            ]
        }
    
    async def assess_quality(self, image: Image.Image, detected_items: List[Dict]) -> Dict:
        """Assess food quality and freshness"""
        quality_scores = {}
        
        for item in detected_items:
            food_type = item['item']
            
            # Simulate quality assessment based on food type
            if food_type in ['salad', 'vegetables']:
                freshness_score = self.assess_freshness_by_color(image, item)
                quality_scores[food_type] = {
                    'freshness': freshness_score,
                    'appearance': min(freshness_score + 0.1, 1.0),
                    'overall_quality': freshness_score
                }
            else:
                # For cooked foods, assess based on appearance
                appearance_score = self.assess_appearance(image, item)
                quality_scores[food_type] = {
                    'freshness': 0.8,  # Assume cooked foods are fresh
                    'appearance': appearance_score,
                    'overall_quality': appearance_score
                }
        
        overall_quality = np.mean([score['overall_quality'] for score in quality_scores.values()])
        
        return {
            'overall_score': overall_quality,
            'item_scores': quality_scores,
            'recommendations': self.generate_quality_recommendations(quality_scores)
        }
    
    def assess_freshness_by_color(self, image: Image.Image, item: Dict) -> float:
        """Assess freshness based on color analysis"""
        # In production, this would analyze color distribution
        # For demo, return mock score
        return 0.85
    
    def assess_appearance(self, image: Image.Image, item: Dict) -> float:
        """Assess food appearance quality"""
        # In production, this would analyze texture, color, etc.
        # For demo, return mock score
        return 0.90
    
    def generate_quality_recommendations(self, quality_scores: Dict) -> List[str]:
        """Generate recommendations based on quality assessment"""
        recommendations = []
        
        for food_type, scores in quality_scores.items():
            if scores['freshness'] < 0.7:
                recommendations.append(f"The {food_type} appears less fresh than optimal")
            if scores['appearance'] < 0.8:
                recommendations.append(f"The {food_type} presentation could be improved")
        
        if not recommendations:
            recommendations.append("All items appear fresh and well-prepared")
        
        return recommendations
    
    def get_portion_multiplier(self, portion_size: str) -> float:
        """Get nutrition multiplier based on portion size"""
        multipliers = {
            'small': 0.7,
            'medium': 1.0,
            'large': 1.5,
            'extra_large': 2.0,
            'side': 0.5
        }
        return multipliers.get(portion_size, 1.0)
    
    def calculate_confidence(self, detected_items: List[Dict]) -> float:
        """Calculate overall confidence in analysis"""
        if not detected_items:
            return 0.0
        
        confidences = [item['confidence'] for item in detected_items]
        return np.mean(confidences)
    
    async def compare_with_menu_item(self, image_data: bytes, menu_item_id: str) -> Dict:
        """Compare food image with expected menu item"""
        analysis = await self.analyze_food_image(image_data)
        menu_item = await self.get_menu_item(menu_item_id)
        
        if not analysis['success']:
            return {'match': False, 'confidence': 0.0, 'reason': 'Analysis failed'}
        
        detected_items = analysis['detected_items']
        if not detected_items:
            return {'match': False, 'confidence': 0.0, 'reason': 'No items detected'}
        
        # Check if any detected item matches the menu item
        menu_item_name = menu_item.get('name', '').lower()
        for item in detected_items:
            if menu_item_name in item['item'] or item['item'] in menu_item_name:
                return {
                    'match': True,
                    'confidence': item['confidence'],
                    'detected_item': item['item'],
                    'menu_item': menu_item_name
                }
        
        return {
            'match': False,
            'confidence': max(item['confidence'] for item in detected_items),
            'reason': f"Detected {[item['item'] for item in detected_items]}, expected {menu_item_name}"
        }
    
    async def get_menu_item(self, menu_item_id: str) -> Dict:
        """Get menu item details"""
        # In production, this would query the database
        return {
            'id': menu_item_id,
            'name': 'Margherita Pizza',
            'description': 'Classic pizza with tomato sauce and mozzarella',
            'category': 'pizza'
      }
