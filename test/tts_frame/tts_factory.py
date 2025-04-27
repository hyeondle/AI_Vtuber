from .edge_tts import EdgeTTS
# from .coqui_tts_client import CoquiTTS (나중에 추가)
# from .bark_tts_client import BarkTTS (나중에 추가)

def create_tts_engine(name: str):
    if name == "edge":
        return EdgeTTS()
    # elif name == "coqui":
    #     return CoquiTTS()
    # elif name == "bark":
    #     return BarkTTS()
    else:
        raise ValueError(f"지원하지 않는 TTS 엔진: {name}")
