# src/food_delivery_platform.py
"""
Main Food Delivery Platform class that integrates all components
"""

import asyncio
import logging
from typing import Dict, List, Optional

from .models import Location, OrderStatus
from .services import (
    OrderService, RealTimeDeliveryService, RecommendationService,
    CustomerSupportService, FoodRecognitionService, AnalyticsService,
    CacheService
)
from .ml_models import (
    AdvancedFoodRecommender, QuantumInspiredDeliveryOptimizer,
    DeliveryTimePredictor, FederatedLearningSystem
)
from .api import OrderAPI, RecommendationAPI, CustomerSupportAPI, WebSocketManager

logger = logging.getLogger(__name__)

class FoodDeliveryPlatform:
    """
    Complete Food Delivery Platform integrating all advanced features
    """
    
    def __init__(self):
        # Initialize core services
        self.order_service = OrderService()
        self.delivery_service = RealTimeDeliveryService()
        self.recommendation_service = RecommendationService()
        self.customer_support_service = CustomerSupportService()
        self.food_recognition_service = FoodRecognitionService()
        self.analytics_service = AnalyticsService()
        self.cache_service = CacheService()
        
        # Initialize ML models
        self.recommendation_engine = AdvancedFoodRecommender(10000, 5000)
        self.delivery_optimizer = QuantumInspiredDeliveryOptimizer()
        self.delivery_predictor = DeliveryTimePredictor()
        self.federated_learning = FederatedLearningSystem(100)
        
        # Initialize API endpoints
        self.order_api = OrderAPI(self.order_service)
        self.recommendation_api = RecommendationAPI(self.recommendation_service)
        self.customer_support_api = CustomerSupportAPI(self.customer_support_service)
        
        # Initialize WebSocket manager for real-time updates
        self.websocket_manager = WebSocketManager()
        
        # Platform state
        self.is_initialized = False
        self.background_tasks = []
        
        logger.info("Food Delivery Platform instance created")
    
    async def initialize(self):
        """Initialize the platform and all its components"""
        if self.is_initialized:
            logger.warning("Platform already initialized")
            return
        
        try:
            logger.info("Initializing Food Delivery Platform...")
            
            # Train ML models with synthetic data for demo
            await self.initialize_ml_models()
            
            # Start background tasks
            await self.start_background_tasks()
            
            self.is_initialized = True
            logger.info("Food Delivery Platform initialized successfully!")
            
        except Exception as e:
            logger.error(f"Platform initialization failed: {e}")
            raise
    
    async def initialize_ml_models(self):
        """Initialize and train ML models"""
        logger.info("Initializing ML models...")
        
        # Train recommendation model
        await asyncio.get_event_loop().run_in_executor(
            None, self.recommendation_engine.train_with_synthetic_data
        )
        
        # Train delivery time predictor
        await asyncio.get_event_loop().run_in_executor(
            None, self.delivery_predictor.train_with_synthetic_data
        )
        
        # Initialize federated learning
        model_architecture = {
            'dense_1': {'type': 'dense', 'input_dim': 64, 'output_dim': 32},
            'dense_2': {'type': 'dense', 'input_dim': 32, 'output_dim': 16},
            'output': {'type': 'dense', 'input_dim': 16, 'output_dim': 1}
        }
        await self.federated_learning.initialize_global_model(model_architecture)
        
        logger.info("ML models initialized successfully")
    
    async def start_background_tasks(self):
        """Start background maintenance tasks"""
        # Analytics monitoring
        analytics_task = asyncio.create_task(self.background_analytics())
        self.background_tasks.append(analytics_task)
        
        # Model retraining
        retraining_task = asyncio.create_task(self.periodic_model_retraining())
        self.background_tasks.append(retraining_task)
        
        # Cache cleanup
        cache_cleanup_task = asyncio.create_task(self.periodic_cache_cleanup())
        self.background_tasks.append(cache_cleanup_task)
        
        logger.info("Background tasks started")
    
    async def background_analytics(self):
        """Background task for continuous analytics"""
        while True:
            try:
                health_report = await self.analytics_service.get_system_health()
                
                # Log system health periodically
                if health_report['status'] != 'healthy':
                    logger.warning(f"System health degraded: {health_report['status']}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Background analytics error: {e}")
                await asyncio.sleep(10)
    
    async def periodic_model_retraining(self):
        """Periodic retraining of ML models"""
        while True:
            try:
                logger.info("Starting periodic model retraining...")
                
                # Retrain recommendation model
                await asyncio.get_event_loop().run_in_executor(
                    None, self.recommendation_engine.train_with_synthetic_data, 5
                )
                
                # Retrain delivery predictor
                await asyncio.get_event_loop().run_in_executor(
                    None, self.delivery_predictor.train_with_synthetic_data, 5
                )
                
                logger.info("Periodic model retraining completed")
                await asyncio.sleep(24 * 60 * 60)  # Retrain daily
                
            except Exception as e:
                logger.error(f"Model retraining error: {e}")
                await asyncio.sleep(60 * 60)  # Retry in 1 hour
    
    async def periodic_cache_cleanup(self):
        """Periodic cleanup of expired cache entries"""
        while True:
            try:
                cleared_count = await self.cache_service.clear_expired()
                if cleared_count > 0:
                    logger.info(f"Cleared {cleared_count} expired cache entries")
                
                await asyncio.sleep(5 * 60)  # Clean every 5 minutes
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
                await asyncio.sleep(60)
    
    # Core Platform Methods
    async def place_order(self, user_id: str, restaurant_id: str, 
                         items: List[Dict], delivery_address: Dict) -> Dict:
        """Main method to place an order"""
        try:
            # Validate inputs
            await self.validate_order_inputs(user_id, restaurant_id, items, delivery_address)
            
            # Create order data
            order_data = {
                'user_id': user_id,
                'restaurant_id': restaurant_id,
                'items': items,
                'delivery_address': delivery_address,
                'total_amount': self.calculate_order_total(items),
                'created_at': asyncio.get_event_loop().time()
            }
            
            # Use OrderAPI to place order
            api_result = await self.order_api.place_order(order_data)
            
            if api_result['success']:
                # Track successful order in analytics
                await self.analytics_service.track_order_metric('order_placed', 1, {
                    'user_id': user_id,
                    'restaurant_id': restaurant_id,
                    'order_value': order_data['total_amount']
                })
            
            return api_result
            
        except Exception as e:
            # Track failed order in analytics
            await self.analytics_service.track_order_metric('order_failed', 1, {
                'error': str(e),
                'user_id': user_id
            })
            
            logger.error(f"Order placement failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Order placement failed'
            }
    
    async def get_personalized_recommendations(self, user_id: str, 
                                             latitude: float, longitude: float) -> Dict:
        """Get personalized restaurant recommendations"""
        return await self.recommendation_api.get_recommendations(
            user_id, latitude, longitude
        )
    
    async def process_customer_query(self, query_data: Dict) -> Dict:
        """Process customer support query"""
        return await self.customer_support_api.process_support_query(query_data)
    
    async def analyze_food_image(self, image_data: bytes) -> Dict:
        """Analyze food image for recognition and nutrition"""
        # This would use FoodRecognitionAPI in production
        return await self.food_recognition_service.analyze_food_image(image_data)
    
    async def get_order_status(self, order_id: str) -> Dict:
        """Get comprehensive order status"""
        return await self.order_api.get_order_status(order_id)
    
    async def update_order_status(self, order_id: str, new_status: str, 
                                metadata: Dict = None) -> Dict:
        """Update order status with real-time notifications"""
        api_result = await self.order_api.update_order_status(
            order_id, new_status, metadata
        )
        
        if api_result['success']:
            # Broadcast real-time update via WebSocket
            await self.websocket_manager.broadcast_order_update(
                order_id, new_status, metadata
            )
            
            # Track status update in analytics
            await self.analytics_service.track_order_metric('order_status_update', 1, {
                'order_id': order_id,
                'new_status': new_status
            })
        
        return api_result
    
    async def assign_delivery(self, order: Dict) -> Dict:
        """Assign delivery partner to order"""
        try:
            delivery_partner = await self.delivery_service.assign_delivery(order)
            
            if delivery_partner:
                return {
                    'success': True,
                    'delivery_partner': delivery_partner,
                    'message': 'Delivery assigned successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'No available delivery partners',
                    'message': 'Delivery assignment failed'
                }
                
        except Exception as e:
            logger.error(f"Delivery assignment failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Delivery assignment failed'
            }
    
    # Utility Methods
    async def validate_order_inputs(self, user_id: str, restaurant_id: str, 
                                  items: List[Dict], delivery_address: Dict):
        """Validate order inputs before processing"""
        if not user_id or not restaurant_id:
            raise ValueError("User ID and Restaurant ID are required")
        
        if not items:
            raise ValueError("Order must contain at least one item")
        
        if not delivery_address:
            raise ValueError("Delivery address is required")
        
        # Validate location
        if 'latitude' not in delivery_address or 'longitude' not in delivery_address:
            raise ValueError("Delivery address must contain latitude and longitude")
    
    def calculate_order_total(self, items: List[Dict]) -> float:
        """Calculate order total with taxes and fees"""
        subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
        delivery_fee = 5.0  # Base delivery fee
        tax = subtotal * 0.08  # 8% tax
        
        return round(subtotal + delivery_fee + tax, 2)
    
    async def get_system_health(self) -> Dict:
        """Get comprehensive system health report"""
        try:
            health_report = await self.analytics_service.get_system_health()
            
            # Add platform-specific health information
            health_report['platform'] = {
                'initialized': self.is_initialized,
                'background_tasks_running': len(self.background_tasks),
                'websocket_connections': self.websocket_manager.get_connection_stats(),
                'cache_stats': await self.cache_service.get_stats(),
                'federated_learning_stats': self.federated_learning.get_system_stats()
            }
            
            return health_report
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': asyncio.get_event_loop().time()
            }
    
    async def get_business_insights(self) -> Dict:
        """Get business insights and analytics"""
        return await self.analytics_service.get_business_insights()
    
    async def shutdown(self):
        """Gracefully shutdown the platform"""
        logger.info("Shutting down Food Delivery Platform...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        self.is_initialized = False
        logger.info("Food Delivery Platform shutdown completed")
