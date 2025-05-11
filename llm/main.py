from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
import json
from dotenv import load_dotenv
from google import genai
import os
from db import init_db, get_or_create_user, save_history_to_db, show_all_db_histories
from memory import save_to_redis, get_history_from_redis, show_all_redis_histories
import redis.asyncio as redis
from prompt import pre_prompt, init_prompt

import asyncio

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"
chat = None
app = FastAPI()
user_id = None

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

@app.on_event("startup")
async def startup():
    await init_db()
    await redis_client.ping()
    print("[LLM] ✅ DB 초기화 완료", flush=True)

    global chat
    chat = client.chats.create(model=model)

@app.post("/llm/init_user")
async def init_user(request: Request):
    data = await request.json()
    global user_id
    user_id = data.get("user_id", "").strip()
    if not user_id:
        return JSONResponse(content={"error": "Missing user_id"}, status_code=400)

    user, past_history = await get_or_create_user(user_id)
    history_prompt = []
    for item in past_history:
        fole = item["role"]
        text = item["text"]
        history_prompt.append(f"{role}: {text.strip()}")

    history_prompt += init_prompt
    response = chat.send_message(history_prompt)

    if response.text.strip().lower() != "ok":
        print("[LLM] ❌ 초기화 실패", flush=True)
        await ws.close()
        return

    print("[LLM] ✅ 초기화 완료.", flush=True)

@app.websocket("/ws/llm")
async def llm_ws(ws: WebSocket):
    await ws.accept()
    global user_id
    try:
        while True:
            message = await ws.receive_text()
            payload = json.loads(message)
            text = payload.get("text", "")
            prompt = f"user_id : {user_id}\n" + pre_prompt + f"user : {text}"

            print(f"[LLM] 프롬프트 수신: {text}", flush=True)
            try:
                # stream = client.models.generate_content_stream(
                #     model=model,
                #     contents=[prompt]
                # )
                # response = "".join([part.text for part in stream])
                response = chat.send_message(prompt)
            except Exception as e:
                response = f"[ERROR] {e}"
            print("[LLM Raw Response]:", repr(response.text), flush=True)
            await ws.send_text(response.text)

            await save_to_redis(redis_client, user_id, "user", text)
            await save_to_redis(redis_client, user_id, "bot", response.text)

    except WebSocketDisconnect:
        print("[LLM] 연결 해제됨", flush=True)
