import json

async def save_to_redis(redis_client, user_id: str, role: str, text: str):
    await redis_client.rpush(f"history:{user_id}", json.dumps({
        "role": role,
        "text": text
    }))

async def get_history_from_redis(redis_client, user_id: str):
    raw = await redis_client.lrange(f"history:{user_id}", 0, -1)
    return [json.loads(r) for r in raw]

async def show_all_redis_histories(redis_client):
    keys = await redis_client.keys("history:*")
    print(f"\n📦 현재 Redis 히스토리 키 목록: {keys}")
    for key in keys:
        raw_entries = await redis_client.lrange(key, 0, -1)
        entries = [json.loads(r) for r in raw_entries]
        print(f"\n🧾 {key}:")
        for item in entries:
            print(f"  - {item['role']}: {item['text']}")