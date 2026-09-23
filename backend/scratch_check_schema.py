import asyncio
import mongodb

async def check_db():
    db = mongodb.get_db()
    u = await db.users.find_one()
    c = await db.companies.find_one({'company_id': u['company_id']}) if u else None
    print('User keys:', list(u.keys()) if u else None)
    print('Company keys:', list(c.keys()) if c else 'None')
    if c:
        print('Company name:', c.get('name'))

asyncio.run(check_db())
