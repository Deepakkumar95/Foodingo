# src/api/websocket.py
import asyncio
import json
import logging
from typing import Dict, Set, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, Set] = {}
        self.heartbeat_interval = 30  # seconds
        
    async def register_connection(self, connection, user_id: str, order_id: Optional[str] = None):
        """Register a new WebSocket connection"""
        connection_id = id(connection)
        
        if user_id not in self.connections:
            self.connections[user_id] = set()
        
        self.connections[user_id].add(connection)
        
        logger.info(f"WebSocket connection registered for user {user_id}")
        
        # Send welcome message
        welcome_message = {
            'type': 'connection_established',
            'user_id': user_id,
            'connection_id': connection_id,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.send_message(connection, welcome_message)
        
        # Start heartbeat for this connection
        asyncio.create_task(self.heartbeat(connection))
    
    async def unregister_connection(self, connection, user_id: str):
        """Unregister a WebSocket connection"""
        if user_id in self.connections:
            self.connections[user_id].discard(connection)
            
            if not self.connections[user_id]:
                del self.connections[user_id]
        
        logger.info(f"WebSocket connection unregistered for user {user_id}")
    
    async def broadcast_to_user(self, user_id: str, message: Dict):
        """Broadcast message to all connections of a user"""
        if user_id not in self.connections:
            return
        
        connections = self.connections[user_id].copy()
        
        for connection in connections:
            try:
                await self.send_message(connection, message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                await self.unregister_connection(connection, user_id)
    
    async def broadcast_order_update(self, order_id: str, status: str, 
                                   additional_data: Dict = None):
        """Broadcast order update to relevant users"""
        # In production, this would determine which users to notify based on order ownership
        # For demo, we'll assume the order ID contains user information
        user_id = order_id.split('_')[1] if '_' in order_id else 'unknown'
        
        message = {
            'type': 'order_update',
            'order_id': order_id,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'data': additional_data or {}
        }
        
        await self.broadcast_to_user(user_id, message)
        logger.info(f"Order update broadcast for order {order_id}")
    
    async def broadcast_delivery_update(self, delivery_id: str, status: str,
                                      location: Optional[Dict] = None):
        """Broadcast delivery update"""
        # Similar to order update, but for delivery tracking
        message = {
            'type': 'delivery_update',
            'delivery_id': delivery_id,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'location': location
        }
        
        # In production, this would determine which users to notify
        user_id = 'user_123'  # Mock user ID
        
        await self.broadcast_to_user(user_id, message)
        logger.info(f"Delivery update broadcast for delivery {delivery_id}")
    
    async def send_message(self, connection, message: Dict):
        """Send message through WebSocket connection"""
        try:
            if hasattr(connection, 'send_json'):
                await connection.send_json(message)
            elif hasattr(connection, 'send'):
                await connection.send(json.dumps(message))
            else:
                logger.error("Connection object doesn't have send method")
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            raise
    
    async def heartbeat(self, connection):
        """Send heartbeat messages to keep connection alive"""
        try:
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                
                heartbeat_message = {
                    'type': 'heartbeat',
                    'timestamp': datetime.now().isoformat()
                }
                
                await self.send_message(connection, heartbeat_message)
                
        except Exception as e:
            logger.debug(f"Heartbeat stopped: {e}")
    
    async def handle_incoming_message(self, connection, user_id: str, message: Dict):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get('type')
            
            if message_type == 'ping':
                # Respond to ping
                response = {
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }
                await self.send_message(connection, response)
                
            elif message_type == 'subscribe_order':
                # Subscribe to order updates
                order_id = message.get('order_id')
                await self.subscribe_to_order(connection, user_id, order_id)
                
            elif message_type == 'unsubscribe_order':
                # Unsubscribe from order updates
                order_id = message.get('order_id')
                await self.unsubscribe_from_order(connection, user_id, order_id)
                
            elif message_type == 'get_order_status':
                # Get current order status
                order_id = message.get('order_id')
                await self.send_order_status(connection, order_id)
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def subscribe_to_order(self, connection, user_id: str, order_id: str):
        """Subscribe connection to order updates"""
        # In production, this would maintain subscription lists
        # For demo, we'll just send a confirmation
        
        response = {
            'type': 'subscription_confirmed',
            'order_id': order_id,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.send_message(connection, response)
        logger.info(f"User {user_id} subscribed to order {order_id}")
    
    async def unsubscribe_from_order(self, connection, user_id: str, order_id: str):
        """Unsubscribe connection from order updates"""
        response = {
            'type': 'unsubscription_confirmed',
            'order_id': order_id,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.send_message(connection, response)
        logger.info(f"User {user_id} unsubscribed from order {order_id}")
    
    async def send_order_status(self, connection, order_id: str):
        """Send current order status to connection"""
        # In production, this would fetch actual order status
        # For demo, return mock status
        
        status_response = {
            'type': 'order_status',
            'order_id': order_id,
            'status': 'preparing',
            'estimated_delivery_time': '2024-01-15T19:30:00Z',
            'timestamp': datetime.now().isoformat()
        }
        
        await self.send_message(connection, status_response)
    
    def get_connection_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        total_connections = sum(len(connections) for connections in self.connections.values())
        
        return {
            'total_users': len(self.connections),
            'total_connections': total_connections,
            'users_with_connections': list(self.connections.keys()),
            'heartbeat_interval': self.heartbeat_interval
        }
