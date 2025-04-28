import asyncio
from send_text import send_text
import websockets

uri = "ws://localhost:8080/ws/"

async def main():
    print("✉️ 텍스트 입력 모드 (exit 입력 시 종료)", flush=True)

    ws = await websockets.connect(uri)
    print("✅ WebSocket 연결 완료. 메시지 전송 실행", flush=True)

    while True:
        text = input(">> ")
        if text.lower() in ("exit", "quit"):
            break
        await send_text(text, ws)
        

    await ws.close()

if __name__ == "__main__":
    asyncio.run(main())
