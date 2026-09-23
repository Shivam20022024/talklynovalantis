import asyncio
import mongodb

async def check():
    db = mongodb.get_db()
    c = await db.campaigns.find_one({'name': 'for birla group'})
    print('Campaign:', c)

asyncio.run(check())
