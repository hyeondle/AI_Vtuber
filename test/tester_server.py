from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

@app.websocket("/ws/test")
async def test_receiver(ws: WebSocket):
    await ws.accept()
    print("[Tester] ✅ 컨트롤러에서 WebSocket 연결 수락됨", flush=True)
    try:
        while True:
            msg = await ws.receive_text()
            print(f"[Tester] 📥 수신 메시지: {msg}", flush=True)
    except WebSocketDisconnect:
        print("[Tester] ❌ 연결 끊김", flush=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
