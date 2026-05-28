# src/ml_models/delivery_time_predictor.py
import tensorflow as tf
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class DeliveryTimePredictor:
    def __init__(self):
        self.model = self.build_prediction_model()
        self.is_trained = False
        self.feature_names = [
            'distance_to_restaurant', 'distance_to_customer', 'hour_of_day',
            'day_of_week', 'is_peak_hour', 'restaurant_prep_time',
            'restaurant_busy_level', 'partner_rating', 'partner_experience',
            'partner_completed_deliveries', 'traffic_level', 'weather_condition',
            'num_items', 'order_amount'
        ]
        
    def build_prediction_model(self):
        """Build ML model for delivery time prediction"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(14,)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear')  # Predict minutes
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        logger.info("Delivery time prediction model built successfully")
        return model
    
    def prepare_prediction_features(self, order: Dict, delivery_partner: Dict, 
                                  traffic_data: Dict, weather_data: Dict) -> np.ndarray:
        """Prepare features for delivery time prediction"""
        features = []
        
        # Distance features
        restaurant_loc = order.get('restaurant_location')
        customer_loc = order.get('delivery_address')
        partner_loc = delivery_partner.get('location')
        
        if restaurant_loc and partner_loc:
            distance_to_restaurant = self.calculate_distance(partner_loc, restaurant_loc)
        else:
            distance_to_restaurant = 2.0  # Default distance
        
        if restaurant_loc and customer_loc:
            distance_to_customer = self.calculate_distance(restaurant_loc, customer_loc)
        else:
            distance_to_customer = 3.0  # Default distance
        
        features.extend([distance_to_restaurant, distance_to_customer])
        
        # Time features
        order_time = order.get('created_at')
        if order_time:
            hour = order_time.hour
            day_of_week = order_time.weekday()
        else:
            hour = 12
            day_of_week = 0
        
        features.extend([
            hour,
            day_of_week,
            1 if 11 <= hour <= 13 or 18 <= hour <= 20 else 0  # Peak hour
        ])
        
        # Restaurant features
        features.extend([
            order.get('restaurant', {}).get('avg_preparation_time', 15),
            order.get('restaurant', {}).get('busy_level', 0.5)
        ])
        
        # Delivery partner features
        features.extend([
            delivery_partner.get('rating', 4.0),
            delivery_partner.get('experience_months', 12),
            delivery_partner.get('completed_deliveries', 100)
        ])
        
        # Traffic and weather
        features.extend([
            self.traffic_level_to_numeric(traffic_data.get('congestion_level', 'medium')),
            self.weather_condition_to_numeric(weather_data.get('condition', 'clear'))
        ])
        
        # Order features
        features.append(len(order.get('items', [])))
        features.append(order.get('total_amount', 25.0))
        
        return np.array(features).reshape(1, -1)
    
    def calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two locations in km"""
        # Simplified distance calculation
        # In production, use proper geospatial distance
        lat_diff = loc1.latitude - loc2.latitude
        lon_diff = loc1.longitude - loc2.longitude
        return (lat_diff**2 + lon_diff**2)**0.5 * 111  # Approximate km per degree
    
    def traffic_level_to_numeric(self, traffic_level: str) -> float:
        """Convert traffic level to numeric value"""
        levels = {
            'low': 1.0,
            'medium': 1.3,
            'high': 1.7,
            'very_high': 2.2
        }
        return levels.get(traffic_level, 1.5)
    
    def weather_condition_to_numeric(self, weather_condition: str) -> float:
        """Convert weather condition to numeric value"""
        conditions = {
            'clear': 1.0,
            'cloudy': 1.1,
            'rain': 1.4,
            'heavy_rain': 1.8,
            'storm': 2.5,
            'fog': 1.3
        }
        return conditions.get(weather_condition, 1.2)
    
    def predict_delivery_time(self, order: Dict, delivery_partner: Dict, 
                            traffic_data: Dict, weather_data: Dict) -> float:
        """Predict delivery time in minutes"""
        try:
            if not self.is_trained or self.model is None:
                logger.warning("Model not trained or unavailable, using baseline prediction")
                return self.baseline_prediction(order, delivery_partner)
            
            features = self.prepare_prediction_features(
                order, delivery_partner, traffic_data, weather_data
            )
            
            prediction = self.model.predict(features, verbose=0)[0][0]
            
            # Add safety buffer (10%) and ensure minimum time
            predicted_time = max(prediction * 1.1, 15)  # Minimum 15 minutes
            
            logger.debug(f"Predicted delivery time: {predicted_time:.1f} minutes")
            return predicted_time
            
        except Exception as e:
            logger.error(f"Delivery time prediction failed: {e}")
            return self.baseline_prediction(order, delivery_partner)
    
    def baseline_prediction(self, order: Dict, delivery_partner: Dict) -> float:
        """Baseline prediction when model is not available"""
        base_time = 25  # Base delivery time
        num_items = len(order.get('items', []))
        order_amount = order.get('total_amount', 25)
        
        # Adjust based on order characteristics
        if num_items > 5:
            base_time += 5
        if order_amount > 50:
            base_time += 3
        
        # Adjust based on partner rating
        partner_rating = delivery_partner.get('rating', 4.0)
        if partner_rating < 4.0:
            base_time += 5
        elif partner_rating > 4.5:
            base_time -= 3
        
        return float(base_time)
    
    def train_with_synthetic_data(self, epochs: int = 20):
        """Mark the lightweight predictor as trained for demo purposes."""
        logger.info("Simulating delivery time predictor training in lightweight demo mode...")
        self.is_trained = True
        return None
    
    def save_model(self, filepath: str):
        """Save model placeholder state to file."""
        logger.warning("Save model is not supported in lightweight demo mode.")
    
    def load_model(self, filepath: str):
        """Load model placeholder state from file."""
        logger.warning("Load model is not supported in lightweight demo mode.")
        self.is_trained = True
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance (simplified version)"""
        # In production, this would use proper feature importance analysis
        importance_scores = {
            'distance_to_customer': 0.25,
            'traffic_level': 0.18,
            'distance_to_restaurant': 0.15,
            'restaurant_busy_level': 0.12,
            'weather_condition': 0.10,
            'is_peak_hour': 0.08,
            'partner_rating': 0.05,
            'restaurant_prep_time': 0.04,
            'num_items': 0.02,
            'order_amount': 0.01
        }
        
        return importance_scores
