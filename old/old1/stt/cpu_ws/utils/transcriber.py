# stt/cpu_ws/utils/transcriber.py

import whisper
import tempfile

# 모델 캐시
MODEL_CACHE = {}

def load_model(device="cpu"):
    """모델을 메모리에 로드 (이미 로드된 경우 패스)"""
    if device not in MODEL_CACHE:
        MODEL_CACHE[device] = whisper.load_model("base", device=device)
    return MODEL_CACHE[device]

def transcribe_from_bytes(audio_bytes: bytes, prompt: str = "", device: str = "cpu") -> str:
    """바이트 기반 오디오 입력을 받아 텍스트로 변환"""
    model = MODEL_CACHE.get(device)
    if not model:
        raise RuntimeError(f"🔴 모델이 로드되지 않았습니다: device={device}")

    # prefix 프롬프트 추가 (옵션)
    initial_prompt = (
        """
        If nothing detected, return empty string.\nThis is Korean speech. I'll give you chunked audio.\n
        Please use previous context if provided.\nPrompt:
        """
    ) + (prompt if prompt else "")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        result = model.transcribe(
            tmp.name,
            language="ko",
            temperature=0.0,
            best_of=5,
            beam_size=5,
        )
        return result.get("text", "").strip()
