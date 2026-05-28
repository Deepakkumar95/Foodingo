# src/services/order_service.py
import asyncio
import json
import logging
from typing import Dict, List, Optional
from uuid import uuid4
from datetime import datetime

from sqlalchemy import select

from ..database import get_session
from ..models import Order, OrderEvent, OrderStatus, PaymentStatus
from ..models.orm_models import Order as OrderORM, OrderItem as OrderItemORM
from utils.saga_manager import OrderSagaManager
from utils.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, session_factory=None):
        self.saga_manager = OrderSagaManager()
        self.circuit_breaker = CircuitBreaker()
        self.session_factory = session_factory or get_session

    async def place_order(self, order_data: Dict) -> Dict:
        """Place a new order with saga pattern for distributed transactions"""
        saga_id = await self.saga_manager.start_saga()

        try:
            # Validate order
            await self.validate_order(order_data)

            # Process payment
            payment_result = await self.process_payment(order_data)

            # Create order record
            order = await self.create_order_record(order_data, payment_result)

            # Notify restaurant
            await self.notify_restaurant(order)

            # Commit saga
            await self.saga_manager.commit_saga(saga_id)

            # Emit order placed event
            await self.emit_order_event(order, OrderStatus.PLACED)

            logger.info(f"Order {order.id} placed successfully")
            return order.to_dict()
        except Exception as e:
            await self.saga_manager.rollback_saga(saga_id)
            await self.handle_order_failure(order_data, str(e))
            logger.error(f"Order placement failed: {e}")
            raise
    
    async def update_order_status(self, order_id: str, new_status: OrderStatus, 
                                metadata: Dict = None):
        """Update order status with event sourcing"""
        order = await self.get_order(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        if not self.is_valid_status_transition(order.status, new_status):
            raise ValueError(f"Invalid status transition: {order.status} -> {new_status}")

        with self.session_factory() as session:
            orm_order = session.execute(
                select(OrderORM).where(OrderORM.order_id == order_id)
            ).scalars().first()
            if not orm_order:
                raise ValueError(f"Order {order_id} not found")

            orm_order.status = new_status.value
            orm_order.updated_at = datetime.now()
            session.commit()

        event = OrderEvent(
            order_id=order_id,
            user_id=order.user_id,
            restaurant_id=order.restaurant_id,
            status=new_status,
            timestamp=datetime.now().timestamp(),
            metadata=metadata or {}
        )

        await self.emit_event(event)
        await self.handle_status_change_side_effects(order_id, new_status, metadata)
        
        logger.info(f"Order {order_id} status updated to {new_status}")
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        with self.session_factory() as session:
            orm_order = session.execute(
                select(OrderORM).where(OrderORM.order_id == order_id)
            ).scalars().first()
            if not orm_order:
                return None
            return self._convert_orm_order(orm_order)
    
    async def validate_order(self, order_data: Dict):
        """Validate order data"""
        required_fields = ['user_id', 'restaurant_id', 'items', 'delivery_address']
        for field in required_fields:
            if field not in order_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not order_data['items']:
            raise ValueError("Order must contain at least one item")
    
    async def process_payment(self, order_data: Dict) -> Dict:
        """Process payment for order"""
        # In production, this would integrate with payment gateway
        await asyncio.sleep(0.1)  # Simulate payment processing
        return {
            'payment_id': f"pay_{datetime.now().timestamp()}",
            'status': PaymentStatus.COMPLETED,
            'amount': order_data.get('total_amount', 0)
        }
    
    async def create_order_record(self, order_data: Dict, payment_result: Dict) -> Order:
        """Create order record in database"""
        order_id = order_data.get('id') or f"order_{datetime.now().timestamp()}"
        total_amount = order_data.get('total_amount', 0)
        delivery_address = order_data.get('delivery_address')

        try:
            delivery_address_payload = json.dumps(delivery_address)
        except Exception:
            delivery_address_payload = json.dumps({'address': str(delivery_address)})

        with self.session_factory() as session:
            orm_order = OrderORM(
                order_id=order_id,
                user_id=order_data['user_id'],
                restaurant_id=order_data['restaurant_id'],
                total_amount=total_amount,
                status=OrderStatus.PLACED.value,
                payment_status=payment_result['status'].value if hasattr(payment_result['status'], 'value') else str(payment_result['status']),
                delivery_address=delivery_address_payload
            )
            session.add(orm_order)
            session.flush()

            for item in order_data['items']:
                orm_item = OrderItemORM(
                    order_id=orm_order.id,
                    menu_item_id=item.get('id'),
                    name=item['name'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                session.add(orm_item)

            session.commit()
            session.refresh(orm_order)
            _ = orm_order.items

            return self._convert_orm_order(orm_order)
    
    async def notify_restaurant(self, order: Order):
        """Notify restaurant about new order"""
        # In production, this would send push notification or API call
        logger.info(f"Notified restaurant {order.restaurant_id} about order {order.id}")
    
    async def emit_order_event(self, order: Order, status: OrderStatus):
        """Emit order event for event sourcing"""
        event = OrderEvent(
            order_id=order.id,
            user_id=order.user_id,
            restaurant_id=order.restaurant_id,
            status=status,
            timestamp=datetime.now().timestamp()
        )
        await self.emit_event(event)
    
    async def emit_event(self, event: OrderEvent):
        """Emit event to event bus"""
        # In production, this would publish to Kafka/RabbitMQ
        logger.info(f"Event emitted: {event.status} for order {event.order_id}")
    
    def is_valid_status_transition(self, current: OrderStatus, new: OrderStatus) -> bool:
        """Validate order status transition"""
        valid_transitions = {
            OrderStatus.PLACED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.PICKED_UP],
            OrderStatus.PICKED_UP: [OrderStatus.ON_THE_WAY],
            OrderStatus.ON_THE_WAY: [OrderStatus.DELIVERED],
            OrderStatus.CANCELLED: [],
            OrderStatus.DELIVERED: []
        }
        return new in valid_transitions.get(current, [])
    
    async def handle_status_change_side_effects(self, order_id: str, new_status: OrderStatus, 
                                              metadata: Dict):
        """Handle side effects of status change"""
        # Notify user, update analytics, etc.
        if new_status == OrderStatus.DELIVERED:
            await self.handle_order_delivery(order_id)
        elif new_status == OrderStatus.CANCELLED:
            await self.handle_order_cancellation(order_id, metadata)
    
    async def handle_order_failure(self, order_data: Dict, error: str):
        """Handle order placement failure"""
        logger.error(f"Order failed for user {order_data.get('user_id')}: {error}")

    def _convert_orm_order(self, orm_order: OrderORM) -> Order:
        try:
            delivery_address = json.loads(orm_order.delivery_address) if orm_order.delivery_address else None
        except Exception:
            delivery_address = orm_order.delivery_address

        return Order(
            id=orm_order.order_id,
            user_id=orm_order.user_id,
            restaurant_id=orm_order.restaurant_id,
            items=[item.to_dict() for item in orm_order.items],
            total_amount=orm_order.total_amount,
            status=OrderStatus(orm_order.status),
            payment_status=PaymentStatus(orm_order.payment_status),
            delivery_address=delivery_address,
            created_at=orm_order.created_at,
            updated_at=orm_order.updated_at
        )
    
    async def handle_order_delivery(self, order_id: str):
        """Handle order delivery completion"""
        logger.info(f"Order {order_id} delivered successfully")
    
    async def handle_order_cancellation(self, order_id: str, metadata: Dict):
        """Handle order cancellation"""
        reason = metadata.get('reason', 'Unknown')
        logger.info(f"Order {order_id} cancelled: {reason}")
