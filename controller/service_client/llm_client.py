import httpx

LLM_URL = "http://llm:8000/generate"

# async def send_to_llm(prompt: str) -> str:
#     async with httpx.AsyncClient() as client:
#         try:
#             res = await client.post(LLM_URL, json={"prompt": prompt})
#             return res.json().get("response", "[EMPTY RESPONSE]")
#         except Exception as e:
#             print(f"[LLM Client] 오류: {e}", flush=True)
#             return "[ERROR] LLM 오류"

async def send_to_llm(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(LLM_URL, json={"prompt": prompt})
            print(f"[LLM Client] 응답 수신: {res.status_code} | Body: {res.text}", flush=True)
            return res.json().get("response", "[EMPTY RESPONSE]")
        except Exception as e:
            print(f"[LLM Client] 오류: {e}", flush=True)
            return "[ERROR] LLM 오류"

import websockets
import asyncio

LLM_WS_URI = "ws://llm:8000/ws/llm"

async def send_to_llm_ws(prompt: str) -> str:
    try:
        async with websockets.connect(LLM_WS_URI) as ws:
            await ws.send(prompt)
            response = await ws.receive_text()
            return response
    except Exception as e:
        print(f"[LLM WS Client] 오류: {e}", flush=True)
        return "[ERROR] WebSocket 연결 실패"
