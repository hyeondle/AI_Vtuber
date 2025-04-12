import whisper
import tempfile
import torch

# 추후 GPU 제어용 변수 (기본 False → 컨트롤 패널 연동 예정)
USE_GPU = False

device = "cuda" if USE_GPU and torch.cuda.is_available() else "cpu"
model = whisper.load_model("medium", device=device)

def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
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
