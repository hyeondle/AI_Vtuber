from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from utils.transcriber import transcribe_from_bytes, load_model
import asyncio

app = FastAPI()

@app.on_event("startup")
def startup():
    load_model(device="cpu")

@app.get("/is_ready")
def is_ready():
    return JSONResponse(content={"status": "ok", "model": "cpu"})

@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    print("🔌 STT WebSocket 연결 수립됨 (CPU 모델)")

    buffer = b""
    initial_prompt = ""

    while True:
        try:
            data = await websocket.receive_bytes()
            if data == b"<flush>":
                print("📤 STT 변환 요청됨 (CPU)")
                result = transcribe_from_bytes(buffer, prompt=initial_prompt)
                await websocket.send_json({"text": result})
                initial_prompt += " " + result
                buffer = b""
            else:
                buffer += data

        except Exception as e:
            # 예외 발생 시 연결은 유지하되 클라이언트에 오류 전송
            print(f"⚠️ 예외 발생 (STT CPU WS): {e}")
            try:
                await websocket.send_json({"error": str(e)})
            except:
                pass  # 클라이언트가 이미 닫혔다면 무시하고 계속 유지
