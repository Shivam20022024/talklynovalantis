import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv('.env.local')

async def fetch_agents():
    api_key = os.environ.get("BOLNA_API_KEY")
    if not api_key:
        print("NO API KEY")
        return
        
    url = "https://api.bolna.ai/agent"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            for agent in data:
                print(f"Name: {agent.get('agent_name')} | ID: {agent.get('agent_id')}")

asyncio.run(fetch_agents())
