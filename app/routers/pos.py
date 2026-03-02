"""
POS router — manual endpoint to push/retry pushing orders to Petpooja POS.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order, OrderItem, PaymentStatus, PosStatus
from app.schemas.order_schema import PushToPosRequest, PushToPosResponse
from app.services.petpooja_service import push_order

logger = logging.getLogger(__name__)
router = APIRouter(tags=["POS"])


@router.post("/push_to_pos", response_model=PushToPosResponse)
async def push_to_pos(
    request: PushToPosRequest,
    db: Session = Depends(get_db),
):
    """
    Manually push a confirmed (PAID) order to Petpooja POS.
    Useful for retrying failed POS pushes.
    """
    logger.info(f"Manual POS push requested for order {request.order_id}")

    # ── Find order ──
    order = db.query(Order).filter(Order.order_id == request.order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {request.order_id} not found")

    # ── Validate payment status ──
    if order.payment_status != PaymentStatus.PAID:
        return PushToPosResponse(
            success=False,
            message=f"Cannot push to POS — payment status is {order.payment_status.value}",
            order_id=request.order_id,
            pos_status=order.pos_status.value,
        )

    # ── Check if already sent ──
    if order.pos_status == PosStatus.SENT:
        return PushToPosResponse(
            success=True,
            message=f"Order {request.order_id} already pushed to POS",
            order_id=request.order_id,
            pos_status=PosStatus.SENT.value,
        )

    # ── Format order data ──
    order_dict = {
        "order_id": order.order_id,
        "customer_phone": order.customer_phone,
        "customer_name": order.customer_name,
        "address": order.address,
        "order_type": order.order_type.value,
        "total_amount": order.total_amount,
    }
    items_list = [
        {
            "item_name": item.item_name,
            "variation": item.variation,
            "quantity": item.quantity,
            "price": item.price,
            "final_price": item.final_price,
        }
        for item in order.items
    ]

    # ── Push to POS ──
    try:
        result = await push_order(order_dict, items_list)

        if result["success"]:
            order.pos_status = PosStatus.SENT
            db.commit()
            logger.info(f"Order {request.order_id} pushed to POS (manual)")

            return PushToPosResponse(
                success=True,
                message=f"Order {request.order_id} pushed to POS successfully",
                order_id=request.order_id,
                pos_status=PosStatus.SENT.value,
            )
        else:
            order.pos_status = PosStatus.FAILED
            db.commit()
            logger.error(f"Manual POS push failed: {result['message']}")

            return PushToPosResponse(
                success=False,
                message=result["message"],
                order_id=request.order_id,
                pos_status=PosStatus.FAILED.value,
            )

    except Exception as e:
        order.pos_status = PosStatus.FAILED
        db.commit()
        logger.error(f"POS push exception: {e}")

        return PushToPosResponse(
            success=False,
            message=f"POS push error: {str(e)}",
            order_id=request.order_id,
            pos_status=PosStatus.FAILED.value,
        )
