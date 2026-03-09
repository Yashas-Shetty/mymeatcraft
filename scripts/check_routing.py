import httpx
import json

async def check_account_numbers():
    print("Checking all numbers on Rock8 Account...")
    
    with open(".env", "r") as f:
        env = f.read()
    
    api_key = None
    for line in env.split('\n'):
        if line.startswith('RIGHTSIDE_API_KEY='):
            api_key = line.split('=')[1].strip().strip('"').strip("'")
            break

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.rock8.ai/v1/inbound"
    print(f"GET {url}")
    
    async with httpx.AsyncClient() as c:
        response = await c.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_account_numbers())
