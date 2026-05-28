# src/services/recommendation_service.py
import logging
from typing import Dict, List, Optional
import numpy as np

from ..models import Location
from ..ml_models.recommendation_engine import AdvancedFoodRecommender
from ..services.cache_service import CacheService

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self):
        self.recommendation_engine = AdvancedFoodRecommender(10000, 5000)
        self.cache = CacheService()
        
    async def get_personalized_recommendations(self, user_id: str, 
                                             location: Location) -> List[Dict]:
        """Get personalized restaurant recommendations with caching"""
        cache_key = f"recommendations:{user_id}:{location.latitude}:{location.longitude}"
        
        # Try cache first
        cached_recommendations = await self.cache.get(cache_key)
        if cached_recommendations:
            logger.info(f"Returning cached recommendations for user {user_id}")
            return cached_recommendations
        
        # Generate fresh recommendations
        recommendations = await self._generate_recommendations(user_id, location)
        
        # Cache for 5 minutes
        await self.cache.set(cache_key, recommendations, ttl=300)
        
        logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
        return recommendations
    
    async def _generate_recommendations(self, user_id: str, location: Location) -> List[Dict]:
        """Generate personalized recommendations"""
        # Get user preferences and history
        user_data = await self.get_user_data(user_id)
        
        # Get nearby restaurants
        nearby_restaurants = await self.get_nearby_restaurants(location)
        
        if not nearby_restaurants:
            return await self.get_fallback_recommendations(location)
        
        # Generate recommendations using ML engine
        recommendations = []
        
        for restaurant in nearby_restaurants:
            score = await self.calculate_restaurant_score(user_data, restaurant, location)
            
            if score > 0.5:  # Only recommend if score is above threshold
                recommendations.append({
                    'restaurant': restaurant,
                    'score': score,
                    'reasons': await self.get_recommendation_reasons(user_data, restaurant)
                })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:20]
    
    async def calculate_restaurant_score(self, user_data: Dict, restaurant: Dict, 
                                       location: Location) -> float:
        """Calculate recommendation score for restaurant"""
        base_score = 0.0
        
        # Cuisine preference matching
        cuisine_match = self.calculate_cuisine_match(user_data, restaurant)
        base_score += cuisine_match * 0.4
        
        # Price range matching
        price_match = self.calculate_price_match(user_data, restaurant)
        base_score += price_match * 0.2
        
        # Distance factor
        distance_factor = self.calculate_distance_factor(restaurant['location'], location)
        base_score += distance_factor * 0.2
        
        # Rating factor
        rating_factor = restaurant.get('rating', 0) / 5.0
        base_score += rating_factor * 0.2
        
        return min(base_score, 1.0)
    
    def calculate_cuisine_match(self, user_data: Dict, restaurant: Dict) -> float:
        """Calculate cuisine preference match"""
        user_preferences = user_data.get('preferred_cuisines', [])
        restaurant_cuisines = restaurant.get('cuisine', [])
        
        if not user_preferences:
            return 0.5  # Neutral if no preferences
        
        matches = len(set(user_preferences) & set(restaurant_cuisines))
        return matches / len(user_preferences)
    
    def calculate_price_match(self, user_data: Dict, restaurant: Dict) -> float:
        """Calculate price range match"""
        user_price_range = user_data.get('preferred_price_range', 'medium')
        restaurant_price_range = restaurant.get('price_range', 'medium')
        
        price_levels = {'low': 1, 'medium': 2, 'high': 3}
        user_level = price_levels.get(user_price_range, 2)
        restaurant_level = price_levels.get(restaurant_price_range, 2)
        
        level_diff = abs(user_level - restaurant_level)
        return 1.0 - (level_diff / 2.0)  # Normalize to 0-1
    
    def calculate_distance_factor(self, restaurant_loc: Location, user_loc: Location) -> float:
        """Calculate distance factor (closer = better)"""
        distance = self.calculate_distance(restaurant_loc, user_loc)
        max_distance = 10  # 10km maximum for good score
        
        if distance > max_distance:
            return 0.0
        return 1.0 - (distance / max_distance)
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate distance between two locations in km"""
        lat_diff = loc1.latitude - loc2.latitude
        lon_diff = loc1.longitude - loc2.longitude
        return (lat_diff**2 + lon_diff**2)**0.5 * 111
    
    async def get_user_data(self, user_id: str) -> Dict:
        """Get user data for personalization"""
        # In production, this would query user database
        return {
            'user_id': user_id,
            'preferred_cuisines': ['Italian', 'Indian', 'Chinese'],
            'preferred_price_range': 'medium',
            'order_history': [],
            'dietary_restrictions': []
        }
    
    async def get_nearby_restaurants(self, location: Location, radius_km: int = 10) -> List[Dict]:
        """Get restaurants near location"""
        # In production, this would query database with geospatial index
        return [
            {
                'id': 'restaurant_1',
                'name': 'Mario\'s Italian Kitchen',
                'cuisine': ['Italian', 'Pizza'],
                'location': Location(40.7128, -74.0060),
                'rating': 4.5,
                'price_range': 'medium',
                'delivery_time': '25-35 min'
            },
            {
                'id': 'restaurant_2', 
                'name': 'Spice Garden',
                'cuisine': ['Indian', 'Asian'],
                'location': Location(40.7138, -74.0070),
                'rating': 4.7,
                'price_range': 'medium',
                'delivery_time': '30-40 min'
            }
        ]
    
    async def get_fallback_recommendations(self, location: Location) -> List[Dict]:
        """Get fallback recommendations when no personalized ones available"""
        restaurants = await self.get_nearby_restaurants(location)
        return [{'restaurant': r, 'score': 0.6, 'reasons': ['Popular in your area']} 
                for r in restaurants[:10]]
    
    async def get_recommendation_reasons(self, user_data: Dict, restaurant: Dict) -> List[str]:
        """Get reasons why restaurant is recommended"""
        reasons = []
        
        # Cuisine match
        user_cuisines = user_data.get('preferred_cuisines', [])
        restaurant_cuisines = restaurant.get('cuisine', [])
        common_cuisines = set(user_cuisines) & set(restaurant_cuisines)
        
        if common_cuisines:
            reasons.append(f"Matches your taste for {', '.join(common_cuisines)}")
        
        # High rating
        if restaurant.get('rating', 0) >= 4.5:
            reasons.append("Highly rated by customers")
        
        # Fast delivery
        delivery_time = restaurant.get('delivery_time', '')
        if '15-25' in delivery_time or '20-30' in delivery_time:
            reasons.append("Fast delivery")
        
        return reasons if reasons else ["Good match based on your preferences"]
