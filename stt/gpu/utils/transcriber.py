import whisper
import tempfile

# 전역 모델 캐싱 (단일 인스턴스)
MODEL_CACHE = {}

def model_loaded(device: str = "cuda", check_only: bool = False):
    global MODEL_CACHE
    if check_only:
        return device in MODEL_CACHE
    if device not in MODEL_CACHE:
        MODEL_CACHE[device] = whisper.load_model("medium", device=device)  # medium → base로 교체해도 가능
    return True

def transcribe_audio(audio_bytes: bytes, filename: str, device: str = "cuda") -> str:  # ✅ default: cuda
    model = MODEL_CACHE.get(device)
    if not model:
        raise RuntimeError(f"No model loaded for device: {device}")

    suffix = "." + filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        result = model.transcribe(
            tmp.name,
            language="ko",
            temperature=0.0,
            best_of=5,
            beam_size=5
        )
        return result["text"]
