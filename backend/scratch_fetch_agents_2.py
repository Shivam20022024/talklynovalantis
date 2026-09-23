import os
import asyncio
import aiohttp
from dotenv import load_dotenv
import json

load_dotenv('.env.local')

async def fetch_agents():
    api_key = os.environ.get("BOLNA_API_KEY")
    url = "https://api.bolna.ai/agents"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            text = await resp.text()
            print(text)

asyncio.run(fetch_agents())
