import websockets
import json
from utils.audio_utils import convert_to_wav_buffer

class TinySpeechDetector:
    def __init__(self, ws_url="ws://localhost:5004/ws/detect"):
        self.ws_url = ws_url
        self.websocket = None
        self.connected = False

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.ws_url, max_size=None)
            self.connected = True
            print("🔌 [TINY] WebSocket 연결 성공")
        except Exception as e:
            print(f"❌ [TINY] 연결 실패: {e}")
            self.connected = False

    async def detect(self, pcm_bytes: bytes, sample_rate: int = 16000) -> bool:
        if not self.connected or self.websocket is None:
            await self.connect()
            if not self.connected:
                return False

        wav_buffer = convert_to_wav_buffer(pcm_bytes, sample_rate)

        try:
            print("[TINY] 음성 감지 시도")
            await self.websocket.send(wav_buffer.read())
            print("전송 완료")
            response = await self.websocket.recv()
            print("응답 수신 완료")
            result = json.loads(response)
            return result.get("speech_detected", False)
        except Exception as e:
            print(f"❌ [TINY] WebSocket 오류: {e}")
            self.connected = False
            return False
