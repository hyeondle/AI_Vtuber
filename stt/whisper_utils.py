from faster_whisper import WhisperModel

def init_model():
    return WhisperModel("base", compute_type="int8")

def transcribe_audio(model, audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path, language="ko", beam_size=5)
    return " ".join([seg.text for seg in segments]).strip()