import asyncio
import mongodb
import language_service

async def check():
    db = mongodb.get_db()
    agent = await language_service.get_agent_id_for_language(db, 'Hindi', '209cb85e-5ce7-449e-b32c-ad5ca4c6c635')
    print('agent_id:', agent)

asyncio.run(check())
