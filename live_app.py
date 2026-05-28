
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from typing import Any

from src.api.admin import get_admin_router
from src.api.auth import Token, get_current_user
from src.api.websocket import WebSocketManager
from src.config import CORS_ALLOWED_ORIGINS, ENFORCE_HTTPS, TRUSTED_HOSTS
from src.database import get_session, init_db
from src.food_delivery_platform import FoodDeliveryPlatform
from src.models.data_models import Location
from src.models.orm_models import Restaurant as ORMRestaurant, User as ORMUser, Order as ORMOrder
from src.security import create_access_token
from src.services.user_service import UserService

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Foodingo Live",
    description="Swiggy/Zomato Inspired Food Delivery Platform",
    version="2.0.0"
)

if TRUSTED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)

if ENFORCE_HTTPS:
    app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

platform = FoodDeliveryPlatform()
ws_manager = WebSocketManager()
user_service = UserService()

app.include_router(get_admin_router(platform))

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

restaurants = [
    {
        "id": "r1",
        "name": "Spice Garden",
        "rating": 4.7,
        "delivery_time": "20 mins",
        "cuisine": ["Indian", "Chinese"],
        "description": "Flavorful Indian and Asian fusion favorites.",
        "image": "https://images.unsplash.com/photo-1601924638867-3ec8a9b4f6c1?auto=format&fit=crop&w=900&q=80"
    },
    {
        "id": "r2",
        "name": "Pizza Hub",
        "rating": 4.5,
        "delivery_time": "30 mins",
        "cuisine": ["Italian", "Fast Food"],
        "description": "Wood-fired pizza, garlic bread, and more.",
        "image": "https://images.unsplash.com/photo-1548365328-9b5132e4c511?auto=format&fit=crop&w=900&q=80"
    }
]

orders: Dict[str, Dict] = {}

class OrderItem(BaseModel):
    id: Optional[str]
    name: str
    quantity: int
    price: float

class OrderRequest(BaseModel):
    user_name: str
    restaurant_id: str
    delivery_address: Union[str, Dict[str, Union[str, float]]]
    items: List[OrderItem]

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Foodingo backend platform...")
    init_db()
    try:
        await user_service.create_user(
            user_id="admin",
            password="admin123",
            name="Foodingo Admin",
            email="admin@foodingo.local",
            user_type="admin"
        )
    except ValueError:
        pass
    asyncio.create_task(platform.initialize())
    # Configure rotating audit log handler for admin audit logger
    try:
        logs_dir = Path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        audit_path = logs_dir / "admin_audit.jsonl"
        handler = RotatingFileHandler(str(audit_path), maxBytes=5 * 1024 * 1024, backupCount=5)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
        admin_audit_logger = logging.getLogger('admin_audit')
        admin_audit_logger.setLevel(logging.INFO)
        # Avoid duplicate handlers if reloader restarts
        if not any(isinstance(h, RotatingFileHandler) and getattr(h, 'baseFilename', None) == str(audit_path)
                   for h in admin_audit_logger.handlers):
            admin_audit_logger.addHandler(handler)
    except Exception:
        logger.exception("Failed to configure admin audit rotating file handler")
    # Check Redis connectivity for rate limiter (optional)
    try:
        from src.utils import rate_limiter as rl
        import redis.asyncio as aioredis
        redis_url = rl.REDIS_URL if hasattr(rl, 'REDIS_URL') else None
        if redis_url:
            client = aioredis.from_url(redis_url)
            pong = await client.ping()
            if pong:
                logger.info(f"Redis rate-limiter connected ({redis_url})")
            await client.close()
    except Exception:
        logger.info("Redis not available or not configured; using local rate limiter fallback")

@app.get("/")
async def root():
    return {
        "message": "Foodingo Live API Running",
        "features": [
            "Live Order Tracking",
            "Restaurant Discovery",
            "Real-time WebSockets",
            "FastAPI Backend",
            "Swiggy/Zomato Inspired"
        ]
    }

@app.get("/restaurants")
async def get_restaurants():
    def fetch_restaurants():
        with get_session() as session:
            results = session.execute(select(ORMRestaurant)).scalars().all()
            return [restaurant.to_dict() for restaurant in results]

    return await asyncio.to_thread(fetch_restaurants)




@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        subject=user.user_id,
        extra_claims={"user_type": user.user_type}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_current_user(current_user: ORMUser = Depends(get_current_user)):
    return {"success": True, "user": current_user.to_dict()}

@app.post("/orders")
async def place_order(order: OrderRequest):
    def fetch_restaurant():
        with get_session() as session:
            return session.execute(
                select(ORMRestaurant).where(ORMRestaurant.restaurant_id == order.restaurant_id)
            ).scalars().first()

    restaurant = await asyncio.to_thread(fetch_restaurant)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    delivery_address = order.delivery_address
    if isinstance(delivery_address, str):
        delivery_address = {
            "address_line": delivery_address,
            "latitude": 0.0,
            "longitude": 0.0
        }
    else:
        delivery_address = {
            "address_line": delivery_address.get("address_line") or delivery_address.get("address", ""),
            "latitude": float(delivery_address.get("latitude", 0.0)),
            "longitude": float(delivery_address.get("longitude", 0.0))
        }

    order_payload = {
        "user_id": order.user_name,
        "restaurant_id": order.restaurant_id,
        "delivery_address": delivery_address,
        "items": [item.dict() for item in order.items],
        "total_amount": round(sum(item.quantity * item.price for item in order.items), 2)
    }

    try:
        result = await platform.place_order(
            user_id=order_payload["user_id"],
            restaurant_id=order_payload["restaurant_id"],
            items=order_payload["items"],
            delivery_address=order_payload["delivery_address"]
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "Order placement failed"))

        order_data = result.get("data") or result
        return {
            "success": True,
            "order": order_data
        }
    except Exception as e:
        logger.error(f"Order placement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    order = await platform.order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "success": True,
        "order": order.to_dict()
    }

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str, latitude: float = 0.0, longitude: float = 0.0):
    recommendations = await platform.get_personalized_recommendations(user_id, latitude, longitude)
    return {
        "success": True,
        "recommendations": recommendations
    }

@app.websocket("/ws/orders")
async def websocket_endpoint(websocket: WebSocket, user_id: Optional[str] = "anonymous"):
    await ws_manager.register_connection(websocket, user_id)
    try:
        while True:
            message_text = await websocket.receive_text()
            logger.debug(f"Received WS message from {user_id}: {message_text}")
    except WebSocketDisconnect:
        await ws_manager.unregister_connection(websocket, user_id)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "initialized": platform.is_initialized,
        "app_time": datetime.utcnow().isoformat()
    }


# Note: internal system health endpoint moved into the admin router (src/api/admin.py)
