import whisper
import tempfile

def transcribe_audio(audio_bytes: bytes, filename: str, device: str = "cuda") -> str:
    model = whisper.load_model("medium", device=device)

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
