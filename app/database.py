"""
MongoDB client initialization using Motor.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    """Connect to MongoDB."""
    logger.info("Connecting to MongoDB...")
    db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
    logger.info("Connected to MongoDB -> Database: %s", settings.MONGODB_DB_NAME)

async def close_mongo_connection():
    """Close MongoDB connection."""
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")

def get_db():
    """
    FastAPI dependency that provides the MongoDB database instance.
    """
    return db_instance.db
