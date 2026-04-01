"""
Rightside router — endpoint to configure inbound calling via Rightside AI.
"""
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.services.rightside_service import configure_inbound, build_rightside_payload, update_inbound, delete_inbound

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Rightside"])


class RightsideResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


@router.post("/rightside/sync", response_model=RightsideResponse)
async def sync_rightside():
    """
    Push Meatcraft configuration (prompt + tools) to Rightside AI.
    Call this once to set up the inbound number, or again to update.
    """
    try:
        data = await configure_inbound()
        return RightsideResponse(
            success=True,
            message="Rightside inbound configured successfully!",
            data=data
        )
    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rightside/preview")
async def preview_payload():
    """Preview the payload that will be sent to Rightside (for debugging)."""
    try:
        payload = await build_rightside_payload()
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rightside/webhook")
async def rightside_webhook(request: Request):
    """
    Webhook endpoint called by Rock8 on each inbound call.
    Rock8 POSTs call metadata (including caller phone number) here and expects
    the full agent config (prompt, tools, voice, stt) back in the response.
    """
    try:
        # Parse the incoming JSON body from Rock8 — may contain caller metadata
        try:
            body: Dict[str, Any] = await request.json()
        except Exception:
            body = {}

        # Extract caller number — Rock8 may send it under different field names
        caller_number = (
            body.get("caller_id")
            or body.get("caller_number")
            or body.get("from_number")
            or body.get("caller")
            or body.get("phone_number")
            or ""
        )

        logger.info(f"Rock8 webhook received — caller: {caller_number!r}, body keys: {list(body.keys())}")

        # Build the response payload with the actual caller number injected into the prompt
        payload = await build_rightside_payload(caller_number=caller_number)
        return payload
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rightside/update", response_model=RightsideResponse)
async def update_rightside():
    """
    Update an existing Meatcraft configuration on Rightside AI.
    """
    try:
        data = await update_inbound()
        return RightsideResponse(
            success=True,
            message="Rightside inbound updated successfully!",
            data=data
        )
    except Exception as e:
        logger.error(f"Update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rightside/delete", response_model=RightsideResponse)
async def delete_rightside():
    """
    Delete the existing Meatcraft configuration from Rightside AI.
    """
    try:
        data = await delete_inbound()
        return RightsideResponse(
            success=True,
            message="Rightside inbound deleted successfully!",
            data=data
        )
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
