import asyncio
from app.database import db_instance, connect_to_mongo, close_mongo_connection

async def test():
    await connect_to_mongo()
    doc = await db_instance.db['config'].find_one({'type': 'menu'})
    with open("output.txt", "w", encoding="utf-8") as f:
        if doc:
            for i in doc['data'].get('items', []):
                if 'Chicken Curry' in i['itemname']:
                    f.write(f"Name: {i['itemname']} | Pronunciation: {i.get('pronunciation_guide')}\n")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test())
