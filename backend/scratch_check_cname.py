import asyncio
import mongodb

async def check():
    db = mongodb.get_db()
    c = await db.companies.find_one({'company_id': '209cb85e-5ce7-449e-b32c-ad5ca4c6c635'})
    print('NAME:', c.get('name') if c else 'NONE')

asyncio.run(check())
