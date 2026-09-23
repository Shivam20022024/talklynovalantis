import asyncio
import mongodb
import sys
sys.path.append('routes')
from campaign_routes import list_campaigns

async def check():
    res = await list_campaigns({'company_id': '209cb85e-5ce7-449e-b32c-ad5ca4c6c635'})
    print(res)

asyncio.run(check())
