from faster_whisper import WhisperModel

def init_model():
    return WhisperModel("base", compute_type="int8")

def transcribe_audio(model, audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path, language="ko", beam_size=5)
    result = " ".join([segment.text for segment in segments])
    return result.strip()
