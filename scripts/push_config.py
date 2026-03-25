"""
Script to push prompt.txt and menu.txt to the MongoDB config collection.
Run this script whenever you update the local text files to propagate changes to the DB.
"""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import db_instance, connect_to_mongo, close_mongo_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def push_configs():
    try:
        await connect_to_mongo()
        db = db_instance.db
        if db is None:
            logger.error("Failed to connect to MongoDB.")
            return

        project_root = Path(__file__).parent.parent

        # 1. Push Prompt
        prompt_path = project_root / "prompt.txt"
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()
            
            await db["config"].update_one(
                {"type": "prompt"},
                {"$set": {"content": prompt_content}},
                upsert=True
            )
            logger.info("Successfully pushed prompt.txt to DB.")
        else:
            logger.warning("prompt.txt not found.")

        # 2. Push Menu
        menu_path = project_root / "menu.txt"
        if menu_path.exists():
            with open(menu_path, "r", encoding="utf-8-sig") as f:
                raw_menu = f.read().lstrip("\ufeff\u200b")
                menu_data = json.loads(raw_menu)

            await db["config"].update_one(
                {"type": "menu"},
                {"$set": {"data": menu_data}},
                upsert=True
            )
            logger.info("Successfully pushed menu.txt to DB.")
        else:
            logger.warning("menu.txt not found.")

    except Exception as e:
        logger.error(f"Error pushing configs: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(push_configs())
