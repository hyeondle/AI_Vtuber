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