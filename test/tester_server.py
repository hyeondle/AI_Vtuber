# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn

# app = FastAPI()

# @app.websocket("/ws/test")
# async def test_receiver(ws: WebSocket):
#     await ws.accept()
#     print("[Tester] ✅ 컨트롤러에서 WebSocket 연결 수락됨", flush=True)
#     try:
#         while True:
#             msg = await ws.receive_text()
#             print(f"[Tester] 📥 수신 메시지: {msg}", flush=True)
#     except WebSocketDisconnect:
#         print("[Tester] ❌ 연결 끊김", flush=True)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8080)

# tester_server.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import edge_tts
import os
import io
import wave
import json
from tts_frame.tts_factory import create_tts_engine

app = FastAPI()

TTS_ENGINE_NAME = "edge"
tts_engine = None
OUTPUT_DIR = "/app/output"

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

                # 파일 저장
                filename = f"output_{int(asyncio.get_event_loop().time() * 1000)}.wav"
                filepath = os.path.join(OUTPUT_DIR, filename)

                with open(filepath, "wb") as f:
                    f.write(audio_bytes)

                print(f"[Tester] 💾 오디오 저장 완료: {filepath}", flush=True)

    except WebSocketDisconnect:
        print("[Tester] ❌ WebSocket 연결 끊김", flush=True)
