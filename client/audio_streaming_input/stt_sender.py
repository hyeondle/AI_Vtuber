import wave
import io
import requests

def send_chunk_to_stt(audio_bytes: bytes, stt_url: str, initial_prompt: str = ""):
    # 메모리 기반의 버퍼 생성
    buffer = io.BytesIO()

    # 실제 WAV 형식으로 포맷팅
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)         # Mono 채널
        wf.setsampwidth(2)         # 16-bit (2바이트)
        wf.setframerate(16000)     # 샘플링 레이트: 16kHz
        wf.writeframes(audio_bytes)

    buffer.seek(0)  # 파일 포인터를 처음으로 되돌림

    # multipart/form-data 형태로 전송
    files = {"file": ("chunk.wav", buffer, "audio/wav")}
    data = {"initial_prompt": initial_prompt}

    try:
        res = requests.post(stt_url, files=files, data=data)
        if res.ok:
            return res.json().get("text", "[텍스트 없음]")
        else:
            return f"[오류] {res.status_code}: {res.text}"
    except Exception as e:
        return f"[예외] {str(e)}"
