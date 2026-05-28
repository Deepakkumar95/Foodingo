import os
import logging
import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from .models.orm_models import Base, Restaurant as ORMRestaurant

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./foodingo.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True
)


def get_session():
    return SessionLocal()


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


def init_db():
    create_db_and_tables()
    with get_session() as session:
        existing = session.execute(select(ORMRestaurant)).scalars().first()
        if existing:
            return

        logger.info("Seeding database with demo restaurants")
        sample_restaurants = [
            {
                "restaurant_id": "r1",
                "name": "Spice Garden",
                "description": "Flavorful Indian and Asian fusion favorites.",
                "cuisine": json.dumps(["Indian", "Chinese"]),
                "image": "https://images.unsplash.com/photo-1601924638867-3ec8a9b4f6c1?auto=format&fit=crop&w=900&q=80",
                "rating": 4.7,
                "delivery_time": "20 mins",
                "min_order": 150.0,
                "delivery_fee": 35.0,
                "is_active": True,
                "menu_json": json.dumps([
                    {"id": "m1", "name": "Paneer Tikka", "description": "Smoky paneer cubes with rich masala", "price": 260, "image": "https://images.unsplash.com/photo-1601924638867-3ec8a9b4f6c1?auto=format&fit=crop&w=900&q=80"},
                    {"id": "m2", "name": "Butter Naan", "description": "Soft butter naan baked in clay oven", "price": 60, "image": "https://images.unsplash.com/photo-1512058564366-c9e5b2d63c72?auto=format&fit=crop&w=900&q=80"}
                ])
            },
            {
                "restaurant_id": "r2",
                "name": "Pizza Hub",
                "description": "Wood-fired pizza, garlic bread, and more.",
                "cuisine": json.dumps(["Italian", "Fast Food"]),
                "image": "https://images.unsplash.com/photo-1548365328-9b5132e4c511?auto=format&fit=crop&w=900&q=80",
                "rating": 4.5,
                "delivery_time": "30 mins",
                "min_order": 200.0,
                "delivery_fee": 40.0,
                "is_active": True,
                "menu_json": json.dumps([
                    {"id": "m3", "name": "Margherita Pizza", "description": "Classic tomato & mozzarella delight", "price": 380, "image": "https://images.unsplash.com/photo-1548365328-9b5132e4c511?auto=format&fit=crop&w=900&q=80"},
                    {"id": "m4", "name": "Garlic Breadsticks", "description": "Crispy garlic bread with cheese dip", "price": 120, "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80"}
                ])
            }
        ]

        for restaurant_data in sample_restaurants:
            restaurant = ORMRestaurant(**restaurant_data)
            session.add(restaurant)

        session.commit()
        logger.info("Demo restaurants seeded")
