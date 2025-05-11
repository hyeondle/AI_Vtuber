from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Text, select
from datetime import datetime
import json

Base = declarative_base()
engine = create_async_engine("sqlite+aiosqlite:///./llm_history.db")
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class UserHistory(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    role = Column(String)
    text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_or_create_user(user_id: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(UserHistory).where(UserHistory.user_id == user_id)
        )
        items = result.scalars().all()
        history = [{"role": h.role, "parts": [h.text]} for h in items]
        return user_id, history

async def save_history_to_db(user_id: str, redis_client):
    history_key = f"history:{user_id}"
    entries = await redis_client.lrange(history_key, 0, -1)

    async with SessionLocal() as session:
        for raw in entries:
            r = json.loads(raw)
            session.add(UserHistory(
                user_id=user_id,
                role=r["role"],
                text=r["text"]
            ))
        await session.commit()

    # flush 완료 후 Redis에서 해당 유저의 히스토리 삭제
    await redis_client.delete(history_key)
    print(f"🧹 Redis 키 '{history_key}' 삭제 완료")

async def show_all_db_histories():
    async with SessionLocal() as session:
        result = await session.execute(select(UserHistory))
        rows = result.scalars().all()
        print(f"\n💾 DB에 저장된 전체 대화 내역 ({len(rows)}개):")
        for r in rows:
            print(f"  - [{r.timestamp}] {r.user_id} | {r.role}: {r.text}")