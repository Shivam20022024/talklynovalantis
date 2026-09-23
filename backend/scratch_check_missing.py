import asyncio
import mongodb
import sys

async def check():
    db = mongodb.get_db()
    c = await db.companies.find_one({'company_id': '209cb85e-5ce7-449e-b32c-ad5ca4c6c635'})
    print("Company:", c)
    if not c:
        print("Inserting dummy company for this ID to fix the bug...")
        await db.companies.insert_one({
            'company_id': '209cb85e-5ce7-449e-b32c-ad5ca4c6c635',
            'name': 'Novalantis'
        })
        print("Inserted!")

asyncio.run(check())
