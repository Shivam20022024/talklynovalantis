import asyncio
import mongodb

async def check():
    db = mongodb.get_db()
    p = await db.prompts.find_one({'company_id': '209cb85e-5ce7-449e-b32c-ad5ca4c6c635'})
    if p:
        with open('wm.txt', 'w', encoding='utf-8') as f:
            f.write(p.get('welcome_message', 'None'))
    else:
        with open('wm.txt', 'w', encoding='utf-8') as f:
            f.write('No prompt found')

asyncio.run(check())
