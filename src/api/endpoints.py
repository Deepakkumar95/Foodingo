# src/api/endpoints.py
import logging
from typing import Dict, List, Optional
from datetime import datetime

from ..models import OrderStatus, Location
from ..services import (
    OrderService, RecommendationService, 
    CustomerSupportService, FoodRecognitionService
)

logger = logging.getLogger(__name__)

class OrderAPI:
    def __init__(self, order_service: OrderService):
        self.order_service = order_service
        
    async def place_order(self, request_data: Dict) -> Dict:
        """API endpoint for placing an order"""
        try:
            # Validate request data
            validation_errors = self.validate_order_request(request_data)
            if validation_errors:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_errors
                }
            
            # Place order
            order_result = await self.order_service.place_order(request_data)
            
            return {
                'success': True,
                'data': order_result,
                'message': 'Order placed successfully'
            }
            
        except Exception as e:
            logger.error(f"Order placement failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Order placement failed'
            }
    
    async def get_order_status(self, order_id: str) -> Dict:
        """API endpoint for getting order status"""
        try:
            order = await self.order_service.get_order(order_id)
            
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found',
                    'message': f'Order {order_id} not found'
                }
            
            return {
                'success': True,
                'data': {
                    'order_id': order.id,
                    'status': order.status.value,
                    'created_at': order.created_at.isoformat(),
                    'updated_at': order.updated_at.isoformat(),
                    'items': order.items,
                    'total_amount': order.total_amount
                },
                'message': 'Order status retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Order status retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve order status'
            }
    
    async def update_order_status(self, order_id: str, new_status: str, 
                                metadata: Dict = None) -> Dict:
        """API endpoint for updating order status"""
        try:
            # Validate status
            try:
                status_enum = OrderStatus(new_status)
            except ValueError:
                return {
                    'success': False,
                    'error': f'Invalid status: {new_status}',
                    'message': 'Status update failed'
                }
            
            await self.order_service.update_order_status(
                order_id, status_enum, metadata or {}
            )
            
            return {
                'success': True,
                'message': f'Order status updated to {new_status}',
                'data': {
                    'order_id': order_id,
                    'new_status': new_status,
                    'updated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Order status update failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Status update failed'
            }
    
    def validate_order_request(self, request_data: Dict) -> List[str]:
        """Validate order request data"""
        errors = []
        
        required_fields = ['user_id', 'restaurant_id', 'items', 'delivery_address']
        for field in required_fields:
            if field not in request_data:
                errors.append(f"Missing required field: {field}")
        
        if 'items' in request_data:
            if not isinstance(request_data['items'], list):
                errors.append("Items must be a list")
            elif len(request_data['items']) == 0:
                errors.append("Order must contain at least one item")
            else:
                for i, item in enumerate(request_data['items']):
                    if 'id' not in item or 'quantity' not in item:
                        errors.append(f"Item {i} missing required fields (id, quantity)")
        
        if 'delivery_address' in request_data:
            address = request_data['delivery_address']
            if 'latitude' not in address or 'longitude' not in address:
                errors.append("Delivery address must contain latitude and longitude")
        
        return errors

class RecommendationAPI:
    def __init__(self, recommendation_service: RecommendationService):
        self.recommendation_service = recommendation_service
        
    async def get_recommendations(self, user_id: str, latitude: float, 
                                longitude: float, max_results: int = 20) -> Dict:
        """API endpoint for getting recommendations"""
        try:
            location = Location(latitude=latitude, longitude=longitude)
            
            recommendations = await self.recommendation_service.get_personalized_recommendations(
                user_id, location
            )
            
            return {
                'success': True,
                'data': {
                    'user_id': user_id,
                    'location': {'latitude': latitude, 'longitude': longitude},
                    'recommendations': recommendations[:max_results],
                    'total_count': len(recommendations)
                },
                'message': 'Recommendations retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Recommendation retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve recommendations'
            }
    
    async def get_trending_restaurants(self, latitude: float, longitude: float) -> Dict:
        """API endpoint for getting trending restaurants"""
        try:
            location = Location(latitude=latitude, longitude=longitude)
            
            # This would use a different service method in production
            trending = await self.get_trending_restaurants_impl(location)
            
            return {
                'success': True,
                'data': {
                    'location': {'latitude': latitude, 'longitude': longitude},
                    'trending_restaurants': trending
                },
                'message': 'Trending restaurants retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Trending restaurants retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve trending restaurants'
            }
    
    async def get_trending_restaurants_impl(self, location: Location) -> List[Dict]:
        """Get trending restaurants (implementation)"""
        # In production, this would use actual trending algorithm
        return [
            {
                'id': 'trending_1',
                'name': 'Hot Spot Kitchen',
                'cuisine': ['Fusion', 'Asian'],
                'rating': 4.8,
                'delivery_time': '20-30 min',
                'trending_reason': 'Most ordered this week'
            },
            {
                'id': 'trending_2',
                'name': 'Green Leaf Cafe',
                'cuisine': ['Healthy', 'Vegetarian'],
                'rating': 4.6,
                'delivery_time': '25-35 min',
                'trending_reason': 'Rising in popularity'
            }
        ]

class CustomerSupportAPI:
    def __init__(self, customer_support_service: CustomerSupportService):
        self.customer_support_service = customer_support_service
        
    async def process_support_query(self, query_data: Dict) -> Dict:
        """API endpoint for processing customer support queries"""
        try:
            # Validate query data
            if not query_data.get('text') and not query_data.get('audio'):
                return {
                    'success': False,
                    'error': 'Query must contain text or audio',
                    'message': 'Invalid query format'
                }
            
            response = await self.customer_support_service.process_customer_query(query_data)
            
            return {
                'success': True,
                'data': response,
                'message': 'Query processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Support query processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process support query'
            }
    
    async def submit_feedback(self, feedback_data: Dict) -> Dict:
        """API endpoint for submitting feedback"""
        try:
            # Validate feedback data
            required_fields = ['user_id', 'rating', 'type']
            for field in required_fields:
                if field not in feedback_data:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}',
                        'message': 'Feedback submission failed'
                    }
            
            # Process feedback (in production, this would save to database)
            await self.process_feedback(feedback_data)
            
            return {
                'success': True,
                'message': 'Feedback submitted successfully',
                'data': {
                    'feedback_id': f"feedback_{datetime.now().timestamp()}",
                    'submitted_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Feedback submission failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Feedback submission failed'
            }
    
    async def process_feedback(self, feedback_data: Dict):
        """Process feedback data"""
        # In production, this would save to database and trigger analytics
        logger.info(f"Feedback received: {feedback_data}")

class FoodRecognitionAPI:
    def __init__(self, food_recognition_service: FoodRecognitionService):
        self.food_recognition_service = food_recognition_service
        
    async def analyze_food_image(self, image_data: bytes, metadata: Dict = None) -> Dict:
        """API endpoint for analyzing food images"""
        try:
            if not image_data:
                return {
                    'success': False,
                    'error': 'No image data provided',
                    'message': 'Image analysis failed'
                }
            
            analysis_result = await self.food_recognition_service.analyze_food_image(image_data)
            
            return {
                'success': True,
                'data': analysis_result,
                'message': 'Image analyzed successfully'
            }
            
        except Exception as e:
            logger.error(f"Food image analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Image analysis failed'
            }
    
    async def compare_with_menu(self, image_data: bytes, menu_item_id: str) -> Dict:
        """API endpoint for comparing food image with menu item"""
        try:
            if not image_data:
                return {
                    'success': False,
                    'error': 'No image data provided',
                    'message': 'Image comparison failed'
                }
            
            comparison_result = await self.food_recognition_service.compare_with_menu_item(
                image_data, menu_item_id
            )
            
            return {
                'success': True,
                'data': comparison_result,
                'message': 'Image comparison completed'
            }
            
        except Exception as e:
            logger.error(f"Food image comparison failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Image comparison failed'
          }
