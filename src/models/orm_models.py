import json
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(String(128), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    cuisine = Column(Text, nullable=True)
    image = Column(String(1024), nullable=True)
    rating = Column(Float, nullable=False, default=0.0)
    delivery_time = Column(String(64), nullable=True)
    min_order = Column(Float, nullable=False, default=0.0)
    delivery_fee = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, nullable=False, default=True)
    menu_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    orders = relationship("Order", back_populates="restaurant")

    def to_dict(self):
        return {
            "id": self.id,
            "restaurant_id": self.restaurant_id,
            "name": self.name,
            "description": self.description,
            "cuisine": json.loads(self.cuisine) if self.cuisine else [],
            "image": self.image,
            "rating": self.rating,
            "delivery_time": self.delivery_time,
            "min_order": self.min_order,
            "delivery_fee": self.delivery_fee,
            "is_active": self.is_active,
            "menu": json.loads(self.menu_json) if self.menu_json else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(128), unique=True, index=True, nullable=False)
    user_id = Column(String(256), nullable=False)
    restaurant_id = Column(String(128), ForeignKey("restaurants.restaurant_id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(64), nullable=False, default="placed")
    payment_status = Column(String(64), nullable=False, default="pending")
    delivery_address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    restaurant = relationship("Restaurant", back_populates="orders", lazy="joined")

    def to_dict(self):
        try:
            address = json.loads(self.delivery_address) if self.delivery_address else None
        except Exception:
            address = self.delivery_address

        return {
            "id": self.id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "restaurant_id": self.restaurant_id,
            "total_amount": self.total_amount,
            "status": self.status,
            "payment_status": self.payment_status,
            "delivery_address": address,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(String(128), nullable=True)
    name = Column(String(256), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="items")

    def to_dict(self):
        return {
            "id": self.id,
            "menu_item_id": self.menu_item_id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    email = Column(String(256), nullable=True)
    phone = Column(String(64), nullable=True)
    user_type = Column(String(64), nullable=False, default="customer")
    password_hash = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "user_type": self.user_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
