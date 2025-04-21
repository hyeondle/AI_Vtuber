# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from whisper_utils import init_model, transcribe_audio
# import tempfile
# import os

# app = FastAPI()
# model = None

# @app.on_event("startup")
# async def load_model():
#     global model
#     model = init_model()

# @app.get("/is_ready")
# async def is_ready():
#     return {"status": "ok", "model": "loaded"}

# @app.websocket("/ws/stt")
# async def stt_ws(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             print(f"[STT] 수신 base64 오디오")

#             import base64
#             import uuid
#             audio_data = base64.b64decode(data)

#             temp_path = f"/tmp/{uuid.uuid4()}.wav"
#             with open(temp_path, "wb") as f:
#                 f.write(audio_data)

#             try:
#                 text = transcribe_audio(model, temp_path)
#                 print(f"[STT] 텍스트: {text}")
#             except Exception as e:
#                 text = f"[ERROR] STT 실패: {str(e)}"

#             os.remove(temp_path)
#             await websocket.send_text(text)

#     except WebSocketDisconnect:
#         print("[STT] 연결 종료")

from fastapi import FastAPI, WebSocket
import base64
import tempfile
import os
import json
from whisper_utils import init_model, transcribe_audio

app = FastAPI()
model = None

@app.on_event("startup")
async def startup():
    global model
    model = init_model()

@app.websocket("/ws/stt")
async def stt_ws(ws: WebSocket):
    await ws.accept()
    while True:
        message = await ws.receive_text()
        data = json.loads(message)
        audio_b64 = data["payload"]
        audio_data = base64.b64decode(audio_b64)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_data)
            path = f.name

        try:
            result = transcribe_audio(model, path)
        except Exception as e:
            result = f"[ERROR] {e}"
        finally:
            os.remove(path)

        await ws.send_text(result)