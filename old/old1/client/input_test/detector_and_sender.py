import wave
import io
import requests

TINY_API_URL = "http://localhost:5004/detect"

def convert_to_wav_buffer(audio_bytes: bytes, sample_rate=16000) -> io.BytesIO:
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    buffer.seek(0)
    return buffer

async def is_speech_detected_from_buffer_async(wav_buffer: io.BytesIO) -> bool:
    wav_buffer.seek(0)
    async with httpx.AsyncClient() as client:
        files = {"file": ("chunk.wav", wav_buffer, "audio/wav")}
        try:
            res = await client.post(TINY_API_URL, files=files)
            if res.status_code == 200:
                return res.json().get("speech_detected", False)
            else:
                print(f"[Tiny API 오류] {res.status_code}: {res.text}")
                return False
        except Exception as e:
            print(f"[Tiny API 예외] {str(e)}")
            return False

async def send_chunk_to_stt_from_buffer_async(wav_buffer: io.BytesIO, stt_url: str, initial_prompt: str = "") -> str:
    wav_buffer.seek(0)
    async with httpx.AsyncClient() as client:
        files = {"file": ("chunk.wav", wav_buffer, "audio/wav")}
        data = {"initial_prompt": initial_prompt}
        try:
            res = await client.post(stt_url, files=files, data=data)
            if res.status_code == 200:
                return res.json().get("text", "[텍스트 없음]")
            else:
                return f"[오류] {res.status_code}: {res.text}"
        except Exception as e:
            return f"[예외] {str(e)}"
