import whisper
import tempfile

# 전역 모델 캐싱 (단일 인스턴스)
MODEL_CACHE = {}

def model_loaded(device: str = "cpu", check_only: bool = False):
    global MODEL_CACHE
    if check_only:
        return device in MODEL_CACHE
    if device not in MODEL_CACHE:
        MODEL_CACHE[device] = whisper.load_model("small", device=device)  # medium → base로 교체해도 가능
    return True

def transcribe_audio(audio_bytes: bytes, filename: str, device: str = "cpu", prompt: str = "") -> str:
    model = MODEL_CACHE.get(device)
    if not model:
        raise RuntimeError(f"No model loaded for device: {device}")

    prefix_prompt = "There will be Korean speech. As I give you chunked audio, so you might can't understand full sentence. So, I'll give you the result what you transcribed before. Please use it as a previous context, and transcribe the next chunked audio. Prompt:"
    suffix = "." + filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        result = model.transcribe(
            tmp.name,
            language="ko",
            temperature=0.3,
            best_of=5,
            beam_size=5,
            initial_prompt= prefix_prompt + (prompt if prompt else None)
        )
        return result["text"]
