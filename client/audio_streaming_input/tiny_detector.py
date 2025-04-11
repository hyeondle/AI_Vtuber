import wave
import io
import requests
import tempfile

TINY_API_URL = "http://localhost:5004/detect"  # 포트는 docker-compose에 따라 조정

def is_speech_detected(audio_bytes: bytes) -> bool:
    buffer = io.BytesIO()

    # WAV 형식으로 포맷팅
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(16000)
        wf.writeframes(audio_bytes)

    buffer.seek(0)
    files = {"file": ("chunk.wav", buffer, "audio/wav")}

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
