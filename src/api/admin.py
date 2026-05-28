import asyncio
import logging
import time
import json
from typing import Any, Dict, Optional
from pathlib import Path
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from ..database import get_session
from ..models.orm_models import Order as ORMOrder
from .auth import get_current_admin_user
from ..utils.rate_limiter import check_admin_rate_limit

logger = logging.getLogger(__name__)
admin_audit_logger = logging.getLogger('admin_audit')

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = LOG_DIR / "admin_audit.log"


async def admin_rate_limit(current_user=Depends(get_current_admin_user)):
    # Try Redis-backed limiter, fallback to raising 429 if limiter indicates rate exceeded.
    try:
        await check_admin_rate_limit(current_user.user_id)
    except HTTPException:
        raise
    except Exception:
        # If rate limiter internal error, log and allow (fail-open) to avoid blocking admin.
        logger.exception("Rate limiter backend failure; proceeding with request")
    return True


def get_admin_router(platform: Any) -> APIRouter:
    router = APIRouter(prefix="/admin", tags=["admin"])

    class OrderStatusUpdateRequest(BaseModel):
        status: str
        metadata: Optional[Dict[str, Any]] = None

    @router.get("/orders")
    async def list_all_orders(current_user=Depends(get_current_admin_user)):
        def fetch_orders():
            with get_session() as session:
                results = session.execute(select(ORMOrder)).scalars().all()
                return [order.to_dict() for order in results]

        orders = await asyncio.to_thread(fetch_orders)
        return {"success": True, "orders": orders}

    @router.post("/orders/{order_id}/status")
    async def admin_update_order_status(
        order_id: str,
        request: OrderStatusUpdateRequest,
        current_user=Depends(get_current_admin_user)
    ):
        result = await platform.update_order_status(order_id, request.status, request.metadata or {})
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "Status update failed"))
        return {"success": True, "result": result}

    @router.get("/system_health", include_in_schema=False)
    async def admin_system_health(current_user=Depends(get_current_admin_user),
                                  _rl=Depends(admin_rate_limit)):
        """Admin-only system health endpoint moved from main app.
        Hidden from OpenAPI docs via `include_in_schema=False`."""
        try:
            health = await platform.get_system_health()
            # write structured JSON-line audit entry
            try:
                entry = {
                    "ts": __import__("datetime").datetime.utcnow().isoformat(),
                    "user_id": current_user.user_id,
                    "path": "/admin/system_health",
                    "status": "success"
                }
                admin_audit_logger.info(json.dumps(entry))
            except Exception:
                logger.exception("Failed to write audit log")
            return {"success": True, "health": health}
        except Exception as e:
            try:
                entry = {
                    "ts": __import__("datetime").datetime.utcnow().isoformat(),
                    "user_id": current_user.user_id,
                    "path": "/admin/system_health",
                    "status": "error",
                    "error": str(e)
                }
                admin_audit_logger.info(json.dumps(entry))
            except Exception:
                logger.exception("Failed to write audit log")
            logger.error(f"Admin system health fetch failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return router
