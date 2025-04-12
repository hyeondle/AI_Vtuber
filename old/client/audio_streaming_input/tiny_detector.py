import wave
import io
import requests
import tempfile

TINY_API_URL = "http://localhost:5004/detect"  # 포트는 docker-compose에 따라 조정

def convert_to_wav_buffer(audio_bytes: bytes, sample_rate=16000) -> io.BytesIO:
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    buffer.seek(0)
    return buffer

def is_speech_detected_from_buffer(wav_buffer: io.BytesIO) -> bool:
    wav_buffer.seek(0)  # rewind (중요)
    files = {"file": ("chunk.wav", wav_buffer, "audio/wav")}
    try:
        res = requests.post(TINY_API_URL, files=files)
        if res.ok:
            return res.json().get("speech_detected", False)
        else:
            print(f"[Tiny API 오류] {res.status_code}: {res.text}")
            return False
    except Exception as e:
        print(f"[Tiny API 예외] {str(e)}")
        return False
