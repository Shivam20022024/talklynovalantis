import asyncio
import mongodb

async def main():
    db = mongodb.get_db()
    res = await db.companies.update_many(
        {},
        {"$set": {
            "livekit_config": {
                "url": "wss://talkly-cawxd725.livekit.cloud",
                "api_key": "APIeBA3U8LCx88y",
                "api_secret": "aJnQ4hppFfMpNm5QziXxwWnS7KfPjttLWGaRLNpJX4B"
            }
        }}
    )
    print(f"Updated {res.modified_count} companies with LiveKit Cloud config")

if __name__ == "__main__":
    asyncio.run(main())
