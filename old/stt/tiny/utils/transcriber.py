import whisper
import tempfile

MODEL_CACHE = {}

def load_model(device="cpu"):
    if device not in MODEL_CACHE:
        MODEL_CACHE[device] = whisper.load_model("tiny", device=device)
    return MODEL_CACHE[device]

def detect_speech(audio_bytes: bytes, filename: str, device: str = "cpu") -> bool:
    model = load_model(device)
    suffix = "." + filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        result = model.transcribe(
            tmp.name,
            language="ko",
            temperature=0.0,
            initial_prompt="This is only for sound detect. so, if you find human speaking, please return True. If not, you don't need to return anything. Just return empty string.",
        )
        text = result.get("text", "").strip()
        return bool(text)  # 텍스트가 존재하면 발화 감지됨
