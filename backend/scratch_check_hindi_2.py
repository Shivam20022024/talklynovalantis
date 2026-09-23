import asyncio
import sys
sys.path.append('services')
from language_service import LanguageService
import mongodb

async def check():
    db = mongodb.get_db()
    ls = LanguageService()
    agent = await ls.get_agent_id_for_language(db, 'Hindi', '209cb85e-5ce7-449e-b32c-ad5ca4c6c635')
    print('AGENT_ID:', agent)

asyncio.run(check())
