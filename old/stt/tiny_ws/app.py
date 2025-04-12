from fastapi import FastAPI, WebSocket
from utils.transcriber import detect_speech_from_bytes, load_model
import tempfile
import asyncio

app = FastAPI()

@app.on_event("startup")
def preload_model():
    load_model(device="cpu")

@app.get("/is_ready")
def is_ready():
    return {"status": "ready", "device": "cpu", "model": "tiny"}

@app.websocket("/ws/detect")
async def websocket_detect(websocket: WebSocket):
    await websocket.accept()
    print("🟢 [tiny_ws] WebSocket 연결 수립됨")

    while True:
        try:
            print("수신 대기")
            audio_bytes = await websocket.receive_bytes()
            print("수신 완료")
            with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as tmp:
                tmp.write(audio_bytes)
                tmp.flush()
                detected = detect_speech_from_bytes(tmp.name, device="cpu")
                print("발화 감지 결과:", detected)
                await websocket.send_json({"speech_detected": detected})
                print("발화 감지 결과 전송 완료")

        except Exception as e:
            print(f"[tiny_ws 오류] 예외 발생: {e}")
            # 연결을 종료하지 않고 에러만 기록 후 계속 수신 대기
            await asyncio.sleep(0.5)
