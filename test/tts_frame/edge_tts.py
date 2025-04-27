import edge_tts
import io
from pydub import AudioSegment

class EdgeTTS:
    def __init__(self):
        self.voice = "ko-KR-SunHiNeural"

    async def synthesize(self, text: str) -> bytes:
        communicate = edge_tts.Communicate(text, self.voice)
        stream = communicate.stream()  # ✅ await 제거

        audio_mp3_bytes = b""
        async for chunk in stream:
            if chunk["type"] == "audio":
                audio_mp3_bytes += chunk["data"]

        audio = AudioSegment.from_file(io.BytesIO(audio_mp3_bytes), format="mp3")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav", parameters=["-ar", "16000", "-ac", "1"])

        return wav_io.getvalue()