# src/ml_models/federated_learning.py
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FederatedLearningSystem:
    def __init__(self, num_clients: int = 100):
        self.num_clients = num_clients
        self.global_model = None
        self.client_models = {}
        self.differential_privacy = True
        self.secure_aggregation = True
        self.client_data_sizes = {}
        
    async def initialize_global_model(self, model_architecture: Dict):
        """Initialize global model for federated learning"""
        self.global_model = {
            'weights': self.initialize_weights(model_architecture),
            'architecture': model_architecture,
            'round': 0,
            'total_samples': 0
        }
        logger.info("Global model initialized for federated learning")
    
    def initialize_weights(self, architecture: Dict) -> Dict:
        """Initialize model weights based on architecture"""
        # Simplified weight initialization
        # In production, this would use proper neural network initialization
        weights = {}
        for layer_name, layer_config in architecture.items():
            if layer_config['type'] == 'dense':
                shape = (layer_config['input_dim'], layer_config['output_dim'])
                weights[layer_name] = {
                    'kernel': np.random.normal(0, 0.1, shape),
                    'bias': np.zeros(layer_config['output_dim'])
                }
        return weights
    
    async def federated_training_round(self, client_updates: List[Dict]) -> Dict:
        """Perform one round of federated learning"""
        if not client_updates:
            logger.warning("No client updates received for federated training")
            return self.global_model['weights']
        
        logger.info(f"Starting federated training round with {len(client_updates)} clients")
        
        # Secure aggregation
        if self.secure_aggregation:
            aggregated_update = self.secure_aggregate(client_updates)
        else:
            aggregated_update = self.average_updates(client_updates)
        
        # Apply differential privacy
        if self.differential_privacy:
            aggregated_update = self.add_differential_privacy_noise(aggregated_update)
        
        # Update global model
        self.update_global_model(aggregated_update)
        
        # Update round counter
        self.global_model['round'] += 1
        
        logger.info(f"Federated training round {self.global_model['round']} completed")
        return aggregated_update
    
    def secure_aggregate(self, client_updates: List[Dict]) -> Dict:
        """Secure aggregation of client updates"""
        if not client_updates:
            return {}
        
        aggregated = {}
        
        # Initialize aggregated structure based on first client
        first_client = client_updates[0]
        for key in first_client.keys():
            if key != 'client_id' and key != 'num_samples':
                aggregated[key] = np.zeros_like(first_client[key])
        
        total_samples = 0
        
        # Weighted average based on number of samples
        for update in client_updates:
            num_samples = update.get('num_samples', 1)
            total_samples += num_samples
            
            for key, value in update.items():
                if key != 'client_id' and key != 'num_samples':
                    if key in aggregated:
                        aggregated[key] += value * num_samples
        
        # Normalize by total samples
        for key in aggregated.keys():
            aggregated[key] /= total_samples
        
        return aggregated
    
    def average_updates(self, client_updates: List[Dict]) -> Dict:
        """Simple average of client updates"""
        if not client_updates:
            return {}
        
        aggregated = {}
        num_clients = len(client_updates)
        
        # Initialize aggregated structure
        first_client = client_updates[0]
        for key in first_client.keys():
            if key != 'client_id' and key != 'num_samples':
                aggregated[key] = np.zeros_like(first_client[key])
        
        # Sum all updates
        for update in client_updates:
            for key, value in update.items():
                if key != 'client_id' and key != 'num_samples':
                    if key in aggregated:
                        aggregated[key] += value
        
        # Average
        for key in aggregated.keys():
            aggregated[key] /= num_clients
        
        return aggregated
    
    def add_differential_privacy_noise(self, update: Dict, 
                                     epsilon: float = 1.0, 
                                     delta: float = 1e-5) -> Dict:
        """Add differential privacy noise to aggregated update"""
        if not update:
            return update
        
        noisy_update = {}
        
        for key, value in update.items():
            # Calculate sensitivity (simplified)
            sensitivity = self.calculate_sensitivity(value)
            
            # Calculate sigma for Gaussian mechanism
            sigma = sensitivity * np.sqrt(2 * np.log(1.25 / delta)) / epsilon
            
            # Add Gaussian noise
            noise = np.random.normal(0, sigma, value.shape)
            noisy_update[key] = value + noise
        
        logger.debug("Applied differential privacy noise to model update")
        return noisy_update
    
    def calculate_sensitivity(self, tensor: np.ndarray) -> float:
        """Calculate sensitivity for differential privacy"""
        # Simplified sensitivity calculation
        # In production, this would be based on the clipping norm
        return np.std(tensor) * 0.1
    
    def update_global_model(self, aggregated_update: Dict):
        """Update global model with aggregated update"""
        if not self.global_model:
            logger.error("Global model not initialized")
            return
        
        learning_rate = 0.1  # Federated learning rate
        
        for key, update in aggregated_update.items():
            if key in self.global_model['weights']:
                # Update weights with learning rate
                if 'kernel' in self.global_model['weights'][key]:
                    self.global_model['weights'][key]['kernel'] -= learning_rate * update
                else:
                    self.global_model['weights'][key] -= learning_rate * update
    
    async def get_client_update(self, client_id: str, client_data: Dict) -> Dict:
        """Get model update from a client"""
        if client_id not in self.client_models:
            await self.initialize_client_model(client_id)
        
        client_model = self.client_models[client_id]
        
        # Train client model on local data (simplified)
        client_update = await self.train_client_model(client_model, client_data)
        
        # Record data size for weighted averaging
        self.client_data_sizes[client_id] = len(client_data.get('samples', []))
        client_update['num_samples'] = self.client_data_sizes[client_id]
        client_update['client_id'] = client_id
        
        logger.debug(f"Generated update for client {client_id} with {client_update['num_samples']} samples")
        return client_update
    
    async def initialize_client_model(self, client_id: str):
        """Initialize client model with global model weights"""
        if not self.global_model:
            logger.error("Cannot initialize client model: global model not set")
            return
        
        self.client_models[client_id] = {
            'weights': self.copy_weights(self.global_model['weights']),
            'client_id': client_id
        }
        logger.debug(f"Initialized model for client {client_id}")
    
    def copy_weights(self, weights: Dict) -> Dict:
        """Create a deep copy of model weights"""
        copied = {}
        for key, value in weights.items():
            if isinstance(value, dict):
                copied[key] = {}
                for subkey, subvalue in value.items():
                    copied[key][subkey] = subvalue.copy()
            else:
                copied[key] = value.copy()
        return copied
    
    async def train_client_model(self, client_model: Dict, client_data: Dict) -> Dict:
        """Train client model on local data (simplified)"""
        # In production, this would perform actual training
        # For demo, return a mock update
        
        mock_update = {}
        global_weights = self.global_model['weights']
        
        for key, value in global_weights.items():
            if isinstance(value, dict):
                mock_update[key] = {}
                for subkey, subvalue in value.items():
                    # Create a small random update
                    update_magnitude = 0.01
                    mock_update[key][subkey] = np.random.normal(
                        0, update_magnitude, subvalue.shape
                    )
            else:
                update_magnitude = 0.01
                mock_update[key] = np.random.normal(0, update_magnitude, value.shape)
        
        return mock_update
    
    async def personalize_for_user(self, user_id: str, user_data: Dict) -> Dict:
        """Create personalized model for user"""
        if user_id not in self.client_models:
            await self.initialize_client_model(user_id)
        
        client_model = self.client_models[user_id]
        
        # Fine-tune on user data (simplified)
        personalized_weights = await self.fine_tune_model(client_model, user_data)
        
        logger.info(f"Created personalized model for user {user_id}")
        return personalized_weights
    
    async def fine_tune_model(self, client_model: Dict, user_data: Dict) -> Dict:
        """Fine-tune model on user data"""
        # In production, this would perform actual fine-tuning
        # For demo, return slightly modified weights
        
        fine_tuned_weights = self.copy_weights(client_model['weights'])
        
        # Apply small personalization adjustments
        personalization_strength = 0.05
        
        for key, value in fine_tuned_weights.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    adjustment = np.random.normal(0, personalization_strength, subvalue.shape)
                    fine_tuned_weights[key][subkey] += adjustment
            else:
                adjustment = np.random.normal(0, personalization_strength, value.shape)
                fine_tuned_weights[key] += adjustment
        
        return fine_tuned_weights
    
    def get_system_stats(self) -> Dict:
        """Get federated learning system statistics"""
        return {
            'total_clients': len(self.client_models),
            'global_model_round': self.global_model.get('round', 0) if self.global_model else 0,
            'total_training_samples': sum(self.client_data_sizes.values()),
            'differential_privacy_enabled': self.differential_privacy,
            'secure_aggregation_enabled': self.secure_aggregation,
            'average_samples_per_client': (
                np.mean(list(self.client_data_sizes.values())) 
                if self.client_data_sizes else 0
            )
      }
