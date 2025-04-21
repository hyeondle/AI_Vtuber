import websockets
import asyncio
from utils import convert_to_wav_buffer

async def send_to_ws_server(audio_bytes: bytes, ws_url: str):
    wav_buffer = convert_to_wav_buffer(audio_bytes)

    try:
        async with websockets.connect(ws_url, max_size=None) as websocket:
            await websocket.send(wav_buffer.read())
            response = await websocket.recv()
            return response
    except Exception as e:
        return f"[예외] {e}"
