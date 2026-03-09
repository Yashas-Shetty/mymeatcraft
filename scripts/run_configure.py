import httpx
import asyncio
import json

async def configure():
    api_key = "rock8_c8ce6620f77ca618716f1ceb84f531486924d07ead69ea3e661d3ab480e1fd2f"
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    with open("rock8_config_payload.json", "r", encoding="utf-8") as f:
        payload = json.load(f)
    print("Configuring for:", payload["phone_number"])
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post("https://voice.rock8.ai/inbound/configure", headers=headers, json=payload)
        print("Status:", r.status_code)
        try:
            data = r.json()
            print(json.dumps(data, indent=2))
        except Exception:
            print(r.text[:2000])

asyncio.run(configure())
