import asyncio
from dotenv import load_dotenv
load_dotenv('.env.local')
import mongodb

async def main():
    db = mongodb.get_db()
    cursor = db.usage_records.find({})
    recalculated = 0
    async for u in cursor:
        dur = float(u.get('duration_seconds') or 0.0)
        old_cost = float(u.get('customer_cost') or 0.0)
        old_mins = u.get('billed_minutes')
        
        if dur < 5.0:
            new_cost = 0.0
            new_mins = 0.0
        else:
            new_cost = round(dur * 0.20, 2)
            new_mins = round(dur / 60.0, 2)
            
        if old_cost != new_cost or old_mins != new_mins:
            diff = round(old_cost - new_cost, 2)
            await db.usage_records.update_one(
                {'_id': u['_id']}, 
                {'$set': {'customer_cost': new_cost, 'billed_minutes': new_mins}}
            )
            await db.transactions.update_one(
                {'provider_transaction_id': u.get('call_id')}, 
                {'$set': {'amount': new_cost, 'description': f'Voice usage: {int(round(dur))}s (outbound)'}}
            )
            if diff != 0:
                await db.wallets.update_one(
                    {'company_id': u['company_id']}, 
                    {'$inc': {'balance': diff}}
                )
            recalculated += 1
            print(f"Updated call: {u.get('call_id')} ({dur}s): old INR {old_cost} -> new INR {new_cost} (refunded INR {diff})")
            
    print(f"Done! Successfully recalculated {recalculated} calls to fair per-second billing.")

if __name__ == '__main__':
    asyncio.run(main())
