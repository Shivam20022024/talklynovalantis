import asyncio
import mongodb

async def check():
    db = mongodb.get_db()
    p = await db.prompts.find_one({'company_id': '209cb85e-5ce7-449e-b32c-ad5ca4c6c635'})
    if p:
        print('WM:', repr(p.get('welcome_message')))
        print('PROMPT:', repr(p.get('prompt')))
    else:
        print('No prompt found')

asyncio.run(check())
