import asyncio
import mongodb

async def check():
    db = mongodb.get_db()
    user = await db.users.find_one({'company_id': '209cb85e-5ce7-449e-b32c-ad5ca4c6c635'})
    print('bolna_agent_id:', user.get('bolna_agent_id'))

asyncio.run(check())
