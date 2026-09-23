import asyncio
import mongodb

async def fix():
    db = mongodb.get_db()
    leads = await db.leads.find({'campaign_id': '9efd04af-f01a-43d4-ab7b-d898e352c825'}).to_list(100)
    c = 0
    for lead in leads:
        res = await db.calls.update_many({'call_id': lead['lead_id']}, {'$set': {'campaign_id': '9efd04af-f01a-43d4-ab7b-d898e352c825'}})
        c += res.modified_count
    print('Fixed', c, 'calls')

asyncio.run(fix())
