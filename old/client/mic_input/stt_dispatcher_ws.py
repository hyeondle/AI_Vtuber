import websockets
from utils.audio_utils import convert_to_wav_buffer

class STTDispatcher:
    def __init__(self, ws_url="ws://localhost:5002/ws/transcribe"):
        self.ws_url = ws_url
        self.websocket = None
        self.connected = False
        self.initial_prompt = ""

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.ws_url, max_size=None)
            self.connected = True
            print("🔌 [STT] WebSocket 연결 성공")
        except Exception as e:
            print(f"❌ [STT] 연결 실패: {e}")
            self.connected = False

    async def send_chunk(self, pcm_bytes: bytes, sample_rate: int = 16000) -> str:
        if not self.connected or self.websocket is None:
            await self.connect()
            if not self.connected:
                return "[오류] STT 연결 실패"

        wav_buffer = convert_to_wav_buffer(pcm_bytes, sample_rate)

        try:
            await self.websocket.send(wav_buffer.read())
            await self.websocket.send(b"<flush>")
            response = await self.websocket.recv()
            result = response.strip()
            self.initial_prompt += " " + result
            return result
        except Exception as e:
            print(f"❌ [STT] WebSocket 오류: {e}")
            self.connected = False
            return "[오류] STT 통신 실패"
