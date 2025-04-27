import io
import wave
import numpy as np
import edge_tts
from .tts_interface import TTSEngine

class EdgeTTS(TTSEngine):
    def __init__(self):
        self.voice = "ko-KR-SunHiNeural"
        self.rate = "+0%"

    async def synthesize(self, text: str) -> bytes:
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        stream = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                stream.write(chunk["data"])

        return stream.getvalue()
