import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.rightside_service import sync_rightside_config
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Rightside"])
settings = get_settings()

class RightsideSyncResponse(BaseModel):
    success: bool
    message: str
    data: dict

@router.post("/rightside/sync", response_model=RightsideSyncResponse)
async def sync_config():
    """Sync the Meatcraft configuration to Rightside AI."""
    try:
        data = await sync_rightside_config()
        return RightsideSyncResponse(
            success=True,
            message="Rightside configuration synced successfully!",
            data=data
        )
    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
