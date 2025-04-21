import asyncio
import websockets
import json

async def send_text(text, ws):
    # uri = "ws://localhost:8080/ws"
    # async with websockets.connect(uri) as ws:
    await ws.send(json.dumps({"type": "text", "payload": text}))
    print("[📨] 텍스트 전송 완료", flush=True)