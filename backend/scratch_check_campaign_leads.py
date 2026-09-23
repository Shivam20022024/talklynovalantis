import asyncio
import mongodb

async def check():
    db = mongodb.get_db()
    l = await db.leads.find({'campaign_id': '9efd04af-f01a-43d4-ab7b-d898e352c825'}).to_list(10)
    print('Leads:', l)

asyncio.run(check())
