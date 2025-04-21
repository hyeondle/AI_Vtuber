import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import websockets

async def connect_and_receive():
    uri = "ws://nginx/ws/test"  # nginx 경유
    while True:
        print("🧪 테스트 수신자 연결 시도 중...", flush=True)

        try:
            async with websockets.connect(uri) as ws:
                print("✅ WebSocket 연결 완료. 메시지 수신 대기 중...", flush=True)
                while True:
                    msg = await ws.receive_text()
                    print(f"[🧪 수신 메시지] {msg}", flush=True)
        except Exception as e:
            print(f"❌ 연결 실패 또는 끊김: {e}", flush=True)
            print("🔁 5초 후 재연결 시도...", flush=True)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect_and_receive())

