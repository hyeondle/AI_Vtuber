import whisper

MODEL_CACHE = {}

def load_model(device="cpu"):
    if device not in MODEL_CACHE:
        MODEL_CACHE[device] = whisper.load_model("tiny", device=device)
    return MODEL_CACHE[device]

def detect_speech_from_bytes(file_path: str, device="cpu") -> bool:
    model = load_model(device)
    result = model.transcribe(
        file_path,
        language="ko",
        temperature=0.0,
    )
    print("Transcription result:", result)
    return bool(result.get("text", "").strip())

        # initial_prompt="Detect human voice only. If it's background or noise, return nothing."