# src/models/data_models.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from .enums import OrderStatus, PaymentStatus, UserType

@dataclass
class Location:
    latitude: float
    longitude: float

@dataclass
class OrderEvent:
    order_id: str
    user_id: str
    restaurant_id: str
    status: OrderStatus
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MenuItem:
    id: str
    name: str
    description: str
    price: float
    discounted_price: Optional[float] = None
    image_url: str = ""
    is_vegetarian: bool = False
    is_available: bool = True
    preparation_time: int = 15
    tags: List[str] = field(default_factory=list)
    calories: Optional[int] = None

@dataclass
class User:
    id: str
    email: str
    name: str
    user_type: UserType
    phone: Optional[str] = None
    locations: List[Location] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Restaurant:
    id: str
    name: str
    cuisine: List[str]
    location: Location
    rating: float = 0.0
    delivery_time: str = "30-40 min"
    min_order: float = 0.0
    delivery_fee: float = 0.0
    is_active: bool = True
    menu: List[MenuItem] = field(default_factory=list)

@dataclass
class Order:
    id: str
    user_id: str
    restaurant_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    status: OrderStatus = OrderStatus.PLACED
    payment_status: PaymentStatus = PaymentStatus.PENDING
    delivery_address: Optional[Location] = None
    delivery_partner_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'restaurant_id': self.restaurant_id,
            'items': self.items,
            'total_amount': self.total_amount,
            'status': self.status.value if hasattr(self.status, 'value') else self.status,
            'payment_status': self.payment_status.value if hasattr(self.payment_status, 'value') else self.payment_status,
            'delivery_address': None,
            'delivery_partner_id': self.delivery_partner_id,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }

        if isinstance(self.delivery_address, Location):
            result['delivery_address'] = {
                'latitude': self.delivery_address.latitude,
                'longitude': self.delivery_address.longitude
            }
        elif isinstance(self.delivery_address, dict):
            result['delivery_address'] = self.delivery_address
        else:
            result['delivery_address'] = self.delivery_address

        return result
