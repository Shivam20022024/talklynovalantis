import asyncio
import mongodb
import json

async def check_prompt():
    db = mongodb.get_db()
    prompts = await db.prompts.find().to_list(10)
    with open("prompts.json", "w", encoding="utf-8") as f:
        for p in prompts:
            f.write(json.dumps({
                "prompt": p.get("prompt"),
                "welcome_message": p.get("welcome_message"),
                "company_id": p.get("company_id")
            }, ensure_ascii=False) + "\n")

asyncio.run(check_prompt())
