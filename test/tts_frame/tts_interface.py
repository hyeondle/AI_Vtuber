class TTSEngine:
    async def synthesize(self, text: str) -> bytes:
        raise NotImplementedError("TTS 엔진은 synthesize 메서드를 구현해야 합니다.")
