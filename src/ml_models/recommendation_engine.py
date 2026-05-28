# src/ml_models/recommendation_engine.py
import tensorflow as tf
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class AdvancedFoodRecommender:
    def __init__(self, num_users: int, num_restaurants: int, embedding_dim: int = 64):
        self.num_users = num_users
        self.num_restaurants = num_restaurants
        self.embedding_dim = embedding_dim
        self.model = self.build_transformer_model()
        self.is_trained = False
        
    def build_transformer_model(self):
        """Build transformer-based recommendation model with multiple outputs"""
        # User features input
        user_input = tf.keras.Input(shape=(1,), name='user_id')
        user_embedding = tf.keras.layers.Embedding(
            self.num_users, self.embedding_dim, name='user_embedding'
        )(user_input)
        user_embedding = tf.keras.layers.Flatten()(user_embedding)
        
        # Restaurant features input
        restaurant_input = tf.keras.Input(shape=(1,), name='restaurant_id')
        restaurant_embedding = tf.keras.layers.Embedding(
            self.num_restaurants, self.embedding_dim, name='restaurant_embedding'
        )(restaurant_input)
        restaurant_embedding = tf.keras.layers.Flatten()(restaurant_embedding)
        
        # Contextual features (time, location, etc.)
        context_input = tf.keras.Input(shape=(10,), name='context_features')
        
        # Combine embeddings and context
        combined = tf.keras.layers.Concatenate()(
            [user_embedding, restaurant_embedding, context_input]
        )
        
        # Deep neural network
        x = tf.keras.layers.Dense(256, activation='relu')(combined)
        x = tf.keras.layers.Dropout(0.3)(x)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        
        # Multiple outputs for different objectives
        rating_output = tf.keras.layers.Dense(
            1, activation='sigmoid', name='rating_prediction'
        )(x)
        purchase_output = tf.keras.layers.Dense(
            1, activation='sigmoid', name='purchase_probability'
        )(x)
        
        model = tf.keras.Model(
            inputs=[user_input, restaurant_input, context_input],
            outputs=[rating_output, purchase_output]
        )
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss={
                'rating_prediction': 'mse',
                'purchase_probability': 'binary_crossentropy'
            },
            metrics={
                'rating_prediction': ['mae'],
                'purchase_probability': ['accuracy']
            }
        )
        
        logger.info("Transformer recommendation model built successfully")
        return model
    
    def prepare_context_features(self, user_id: int, restaurant_id: int, 
                               timestamp: float, user_location: Tuple[float, float]) -> np.ndarray:
        """Prepare contextual features for the model"""
        features = []
        
        # Time-based features
        # In production, this would use proper datetime processing
        hour = (timestamp % 86400) / 3600  # Extract hour from timestamp
        features.extend([
            hour,  # Hour of day
            timestamp % 7,  # Day of week
            (timestamp % 365) / 30,  # Month
            1 if 11 <= hour <= 13 or 18 <= hour <= 20 else 0,  # Peak hours
        ])
        
        # User behavior features (simplified)
        user_features = self.get_user_behavior_features(user_id)
        features.extend(user_features)
        
        # Restaurant features (simplified)
        restaurant_features = self.get_restaurant_features(restaurant_id)
        features.extend(restaurant_features)
        
        return np.array(features).reshape(1, -1)
    
    def get_user_behavior_features(self, user_id: int) -> List[float]:
        """Get user behavior features"""
        # In production, this would query user history
        return [
            0.5,  # Avg order value normalized
            0.3,  # Order frequency
            0.8,  # Preference for current cuisine
            0.2,  # Price sensitivity
        ]
    
    def get_restaurant_features(self, restaurant_id: int) -> List[float]:
        """Get restaurant features"""
        # In production, this would query restaurant data
        return [
            0.9,  # Rating normalized
            0.7,  # Popularity
            0.5,  # Price level normalized
            0.3,  # Delivery speed
        ]
    
    def get_real_time_recommendations(self, user_id: int, location: Tuple[float, float], 
                                    max_results: int = 20) -> List[Dict]:
        """Generate real-time personalized recommendations"""
        # This is a simplified version for demo
        # In production, this would query nearby restaurants and score them
        
        if not self.is_trained:
            logger.warning("Model not trained, returning default recommendations")
            return self.get_default_recommendations(max_results)
        
        recommendations = []
        current_timestamp = np.datetime64('now').astype(float) / 1e9
        
        # Mock restaurant data - in production this would come from database
        mock_restaurants = [
            {'id': 1, 'name': 'Italian Bistro', 'cuisine': 'Italian'},
            {'id': 2, 'name': 'Spice Garden', 'cuisine': 'Indian'},
            {'id': 3, 'name': 'Dragon Palace', 'cuisine': 'Chinese'},
            {'id': 4, 'name': 'Burger Hub', 'cuisine': 'American'},
        ]
        
        for restaurant in mock_restaurants:
            # Prepare features
            context_features = self.prepare_context_features(
                user_id, restaurant['id'], current_timestamp, location
            )
            
            # Make prediction (using mock predictions for demo)
            rating_pred = np.random.uniform(0.7, 0.95)
            purchase_prob = np.random.uniform(0.6, 0.9)
            
            # Calculate final score (weighted combination)
            final_score = (
                0.6 * rating_pred +  # Rating importance
                0.4 * purchase_prob  # Purchase probability
            )
            
            recommendations.append({
                'restaurant': restaurant,
                'score': float(final_score),
                'predicted_rating': float(rating_pred),
                'purchase_probability': float(purchase_prob)
            })
        
        # Sort by score and return top results
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:max_results]
    
    def get_default_recommendations(self, max_results: int) -> List[Dict]:
        """Get default recommendations when model is not trained"""
        return [
            {
                'restaurant': {'id': i, 'name': f'Restaurant {i}', 'cuisine': 'Various'},
                'score': 0.8 - (i * 0.1),
                'predicted_rating': 0.8,
                'purchase_probability': 0.7
            }
            for i in range(max_results)
        ]
    
    def train_with_synthetic_data(self, epochs: int = 10):
        """Train model with synthetic data for demo purposes"""
        logger.info("Training recommendation model with synthetic data...")
        
        # Generate synthetic training data
        n_samples = 1000
        user_ids = np.random.randint(0, self.num_users, n_samples)
        restaurant_ids = np.random.randint(0, self.num_restaurants, n_samples)
        
        # Generate context features
        context_features = np.random.random((n_samples, 10))
        
        # Generate synthetic targets
        ratings = np.random.uniform(0.3, 1.0, n_samples)
        purchases = (ratings > 0.7).astype(float)  # Purchase if rating > 0.7
        
        # Train the model
        history = self.model.fit(
            [user_ids, restaurant_ids, context_features],
            [ratings, purchases],
            epochs=epochs,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        self.is_trained = True
        logger.info(f"Model training completed. Final loss: {history.history['loss'][-1]:.4f}")
        
        return history
    
    def predict_rating(self, user_id: int, restaurant_id: int, 
                     context_features: np.ndarray) -> float:
        """Predict rating for user-restaurant pair"""
        if not self.is_trained:
            return 0.5  # Default neutral rating
        
        user_arr = np.array([user_id])
        restaurant_arr = np.array([restaurant_id])
        
        predictions = self.model.predict(
            [user_arr, restaurant_arr, context_features], verbose=0
        )
        return float(predictions[0][0][0])
    
    def predict_purchase_probability(self, user_id: int, restaurant_id: int,
                                  context_features: np.ndarray) -> float:
        """Predict purchase probability for user-restaurant pair"""
        if not self.is_trained:
            return 0.5  # Default neutral probability
        
        user_arr = np.array([user_id])
        restaurant_arr = np.array([restaurant_id])
        
        predictions = self.model.predict(
            [user_arr, restaurant_arr, context_features], verbose=0
        )
        return float(predictions[1][0][0])
    
    def save_model(self, filepath: str):
        """Save model to file"""
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from file"""
        self.model = tf.keras.models.load_model(filepath)
        self.is_trained = True
        logger.info(f"Model loaded from {filepath}")

        """Save model placeholder state to file."""
        logger.warning("Save model is not supported in lightweight demo mode.")
    
    def load_model(self, filepath: str):
        """Load model placeholder state from file."""
        logger.warning("Load model is not supported in lightweight demo mode.")
        self.is_trained = True
