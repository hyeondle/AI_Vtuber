from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from whisper_utils import init_model, transcribe_audio
import tempfile
import os

app = FastAPI()
model = None

@app.on_event("startup")
async def load_model():
    global model
    print("🔄 Whisper 모델 로딩 중...", flush=True)
    model = init_model()
    print("✅ Whisper 모델 로딩 완료 — WebSocket 수신 대기 중...", flush=True)


@app.get("/is_ready")
async def is_ready():
    return {"status": "ok", "model": "loaded"}

@app.websocket("/ws/stt")
async def stt_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🟢 WebSocket 연결됨", flush=True)
    
    try:
        while True:
            data = await websocket.receive_bytes()
            print(f"📥 수신된 오디오 데이터 크기: {len(data)} bytes", flush=True)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(data)
                temp_audio_path = temp_audio.name

            print(f"🎧 임시 오디오 파일 저장: {temp_audio_path}", flush=True)

            try:
                text = transcribe_audio(model, temp_audio_path)
                print(f"📝 인식 결과: {text}", flush=True)
            except Exception as e:
                text = "[ERROR] Whisper STT 실패"
                print(f"❌ STT 오류: {e}", flush=True)

            os.remove(temp_audio_path)
            await websocket.send_text(text)

    except WebSocketDisconnect:
        print("🔌 WebSocket 연결 종료됨", flush=True)
