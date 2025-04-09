import requests
import tempfile

def send_chunk_to_stt(audio_bytes: bytes, stt_url: str, initial_prompt: str = ""):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        with open(tmp.name, "rb") as f:
            files = {"file": f}
            data = {"initial_prompt": initial_prompt}
            try:
                res = requests.post(stt_url, files=files, data=data)
                if res.ok:
                    return res.json().get("text", "[텍스트 없음]")
                else:
                    return f"[오류] {res.status_code}: {res.text}"
            except Exception as e:
                return f"[예외] {str(e)}"