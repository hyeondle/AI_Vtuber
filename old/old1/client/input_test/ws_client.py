import websockets
from utils import convert_to_wav_buffer

class STTWebSocketClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.ws_url, max_size=None)

    async def send_audio(self, audio_bytes: bytes):
        wav_buffer = convert_to_wav_buffer(audio_bytes)
        await self.websocket.send(wav_buffer.read())
        response = await self.websocket.recv()
        return response

    async def close(self):
        if self.websocket:
            await self.websocket.close()
