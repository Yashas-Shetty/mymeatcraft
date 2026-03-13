"""
POS router — manual endpoint to push/retry pushing orders to Petpooja POS.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.models.pydantic_models import PaymentStatus, PosStatus
from app.schemas.order_schema import PushToPosRequest, PushToPosResponse
from app.services.petpooja_service import send_to_petpooja

logger = logging.getLogger(__name__)
router = APIRouter(tags=["POS"])


@router.post("/push_to_pos", response_model=PushToPosResponse)
async def push_to_pos(
    request: PushToPosRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Manually push a confirmed (PAID) order to Petpooja POS.
    Useful for retrying failed POS pushes.
    """
    logger.info(f"Manual POS push requested for order {request.order_id}")

    # ── Find order ──
    order = await db["orders"].find_one({"order_id": request.order_id})
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {request.order_id} not found")

    # ── Validate payment status ──
    if order.get("payment_status") != PaymentStatus.PAID.value:
        return PushToPosResponse(
            success=False,
            message=f"Cannot push to POS — payment status is {order.get('payment_status')}",
            order_id=request.order_id,
            pos_status=order.get("pos_status"),
        )

    # ── Check if already sent ──
    if order.get("pos_status") == PosStatus.SENT.value:
        return PushToPosResponse(
            success=True,
            message=f"Order {request.order_id} already pushed to POS",
            order_id=request.order_id,
            pos_status=PosStatus.SENT.value,
        )

    # ── Push to POS ──
    try:
        class DummyOrderObj: pass
        dummy_order = DummyOrderObj()
        for k, v in order.items():
            setattr(dummy_order, k, v)
        
        class DummyItemObj: pass
        dummy_items = []
        for i in order.get("items", []):
            d_i = DummyItemObj()
            for k, v in i.items():
                setattr(d_i, k, v)
            dummy_items.append(d_i)

        success = await send_to_petpooja(dummy_order, dummy_items)

        if success:
            await db["orders"].update_one(
                {"order_id": request.order_id},
                {"$set": {"pos_status": PosStatus.SENT.value}}
            )
            logger.info(f"Order {request.order_id} pushed to POS (manual)")
            return PushToPosResponse(
                success=True,
                message=f"Order {request.order_id} pushed to POS successfully",
                order_id=request.order_id,
                pos_status=PosStatus.SENT.value,
            )
        else:
            await db["orders"].update_one(
                {"order_id": request.order_id},
                {"$set": {"pos_status": PosStatus.FAILED.value}}
            )
            logger.error(f"Manual POS push failed for {request.order_id}")
            return PushToPosResponse(
                success=False,
                message="POS push failed — check logs for details",
                order_id=request.order_id,
                pos_status=PosStatus.FAILED.value,
            )

    except Exception as e:
        await db["orders"].update_one(
            {"order_id": request.order_id},
            {"$set": {"pos_status": PosStatus.FAILED.value}}
        )
        logger.error(f"POS push exception: {e}")
        return PushToPosResponse(
            success=False,
            message=f"POS push error: {str(e)}",
            order_id=request.order_id,
            pos_status=PosStatus.FAILED.value,
        )
