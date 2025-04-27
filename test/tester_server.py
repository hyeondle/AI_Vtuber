from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import os
import json
import base64
from tts_frame.tts_factory import create_tts_engine

app = FastAPI()

TTS_ENGINE_NAME = "edge"
tts_engine = None
OUTPUT_DIR = "/app/output"
SAVE_AUDIO_LOCALLY = True

@app.on_event("startup")
async def startup():
    global tts_engine
    tts_engine = create_tts_engine(TTS_ENGINE_NAME)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"[Tester] ✅ TTS 엔진 '{TTS_ENGINE_NAME}' 로드 완료", flush=True)

@app.websocket("/ws/test")
async def tts_receiver(ws: WebSocket):
    await ws.accept()
    print("[Tester] ✅ Controller WebSocket 연결 수락됨", flush=True)

    try:
        while True:
            msg = await ws.receive_text()
            parsed = json.loads(msg)
            text = parsed.get("llm_response", "")

            if text:
                print(f"[Tester] 📥 수신한 텍스트: {text}", flush=True)
                audio_bytes = await tts_engine.synthesize(text)

                if SAVE_AUDIO_LOCALLY:
                    filename = f"output_{int(asyncio.get_event_loop().time() * 1000)}.wav"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    with open(filepath, "wb") as f:
                        f.write(audio_bytes)
                    print(f"[Tester] 💾 오디오 저장 완료: {filepath}", flush=True)

                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                await ws.send_text(audio_b64)

                print("[Tester] 📤 Base64 오디오 전송 완료", flush=True)

    except WebSocketDisconnect:
        print("[Tester] ❌ WebSocket 연결 끊김", flush=True)