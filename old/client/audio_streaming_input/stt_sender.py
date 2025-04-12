import wave
import io
import requests

def send_chunk_to_stt_from_buffer(wav_buffer: io.BytesIO, stt_url: str, initial_prompt: str = ""):
    wav_buffer.seek(0)
    files = {"file": ("chunk.wav", wav_buffer, "audio/wav")}
    data = {"initial_prompt": initial_prompt}

    try:
        res = requests.post(stt_url, files=files, data=data)
        if res.ok:
            return res.json().get("text", "[텍스트 없음]")
        else:
            return f"[오류] {res.status_code}: {res.text}"
    except Exception as e:
        return f"[예외] {str(e)}"
