# src/services/delivery_service.py
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..models import Location, Order
from ..ml_models.delivery_optimizer import QuantumInspiredDeliveryOptimizer
from ..ml_models.delivery_time_predictor import DeliveryTimePredictor

logger = logging.getLogger(__name__)

class RealTimeDeliveryService:
    def __init__(self):
        self.optimizer = QuantumInspiredDeliveryOptimizer()
        self.predictor = DeliveryTimePredictor()
        self.active_deliveries = {}
        self.delivery_partners = self.initialize_delivery_partners()
        
    async def assign_delivery(self, order: Dict) -> Optional[Dict]:
        """Assign delivery to optimal delivery partner"""
        try:
            available_partners = await self.get_available_delivery_partners(
                order['restaurant_location']
            )
            
            if not available_partners:
                logger.warning("No available delivery partners")
                return None
            
            # Optimize assignment
            assignment = self.optimizer.optimize_delivery_routes(
                [order], available_partners
            )
            
            if assignment and assignment['routes']:
                assigned_partner = assignment['routes'][0]['delivery_partner']
                await self.update_delivery_assignment(order, assigned_partner)
                
                logger.info(f"Assigned delivery to partner {assigned_partner['id']}")
                return assigned_partner
            
            return None
            
        except Exception as e:
            logger.error(f"Delivery assignment failed: {e}")
            return None
    
    async def get_available_delivery_partners(self, restaurant_location: Location, 
                                            radius_km: int = 5) -> List[Dict]:
        """Get available delivery partners within radius"""
        # In production, this would query database with geospatial index
        available = []
        
        for partner in self.delivery_partners.values():
            if (partner['status'] == 'available' and 
                self.calculate_distance(partner['location'], restaurant_location) <= radius_km):
                available.append(partner)
        
        return available
    
    async def update_delivery_assignment(self, order: Dict, delivery_partner: Dict):
        """Update delivery assignment in system"""
        delivery_id = f"delivery_{datetime.now().timestamp()}"
        
        self.active_deliveries[delivery_id] = {
            'id': delivery_id,
            'order_id': order['id'],
            'delivery_partner_id': delivery_partner['id'],
            'status': 'assigned',
            'assigned_at': datetime.now(),
            'estimated_delivery_time': await self.predict_delivery_time(order, delivery_partner)
        }
        
        # Update partner status
        self.delivery_partners[delivery_partner['id']]['status'] = 'busy'
        
        logger.info(f"Delivery {delivery_id} assigned to partner {delivery_partner['id']}")
    
    async def predict_delivery_time(self, order: Dict, delivery_partner: Dict) -> datetime:
        """Predict delivery time for order"""
        # Get real-time traffic and weather data
        traffic_data = await self.get_traffic_data(order['restaurant_location'])
        weather_data = await self.get_weather_data(order['restaurant_location'])
        
        # Predict delivery time
        minutes = self.predictor.predict_delivery_time(
            order, delivery_partner, traffic_data, weather_data
        )
        
        return datetime.now() + timedelta(minutes=minutes)
    
    async def update_delivery_status(self, delivery_id: str, status: str, 
                                   location: Optional[Location] = None):
        """Update delivery status with optional location update"""
        if delivery_id in self.active_deliveries:
            delivery = self.active_deliveries[delivery_id]
            delivery['status'] = status
            delivery['updated_at'] = datetime.now()
            
            if location:
                delivery['current_location'] = location
            
            # If delivery completed, free up the partner
            if status in ['delivered', 'cancelled']:
                partner_id = delivery['delivery_partner_id']
                if partner_id in self.delivery_partners:
                    self.delivery_partners[partner_id]['status'] = 'available'
            
            logger.info(f"Delivery {delivery_id} status updated to {status}")
    
    async def get_delivery_status(self, order_id: str) -> Optional[Dict]:
        """Get delivery status for order"""
        for delivery in self.active_deliveries.values():
            if delivery['order_id'] == order_id:
                return delivery
        return None
    
    async def get_traffic_data(self, location: Location) -> Dict:
        """Get real-time traffic data for location"""
        # In production, this would call Google Maps API or similar
        return {
            'congestion_level': 'medium',
            'travel_time_index': 1.2
        }
    
    async def get_weather_data(self, location: Location) -> Dict:
        """Get real-time weather data for location"""
        # In production, this would call weather API
        return {
            'condition': 'clear',
            'temperature': 22,
            'precipitation': 0
        }
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate distance between two locations in km"""
        # Simplified calculation - in production use proper geodesic distance
        lat_diff = loc1.latitude - loc2.latitude
        lon_diff = loc1.longitude - loc2.longitude
        return (lat_diff**2 + lon_diff**2)**0.5 * 111  # Approximate km per degree
    
    def initialize_delivery_partners(self) -> Dict:
        """Initialize delivery partners (in production, this would come from database)"""
        return {
            'partner_1': {
                'id': 'partner_1',
                'name': 'John Doe',
                'vehicle_type': 'bike',
                'location': Location(40.7128, -74.0060),
                'status': 'available',
                'rating': 4.8,
                'completed_deliveries': 150
            },
            'partner_2': {
                'id': 'partner_2',
                'name': 'Jane Smith',
                'vehicle_type': 'car',
                'location': Location(40.7138, -74.0070),
                'status': 'available',
                'rating': 4.9,
                'completed_deliveries': 200
            }
                                              }
