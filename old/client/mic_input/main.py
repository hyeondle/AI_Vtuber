import asyncio
from mic_capture import MicCapture
from audio_buffer import SlidingAudioBuffer
from tiny_detector_ws import TinySpeechDetector
from stt_dispatcher_ws import STTDispatcher

BUFFER_DURATION = 2.0  # seconds
OVERLAP_DURATION = 1.0  # seconds
SAMPLE_RATE = 16000

TINY_WS_URL = "ws://localhost:5004/ws/detect"
STT_WS_URL = "ws://localhost:5002/ws/transcribe"

async def main():
    mic = MicCapture()
    buffer = SlidingAudioBuffer(
        sample_rate=SAMPLE_RATE,
        buffer_duration=BUFFER_DURATION,
        overlap=OVERLAP_DURATION
    )

    detector = TinySpeechDetector(ws_url=TINY_WS_URL)
    dispatcher = STTDispatcher(ws_url=STT_WS_URL)

    mic.start()
    print("🎤 실시간 STT 시작")

    while True:
        frame = mic.get_audio_chunk()
        buffer.add_frame(frame)
        if buffer.is_ready():
            chunk = buffer.get_buffer()
            print("🔍 [VAD] 청크 구성 완료 → 발화 감지 중...")

            if await detector.detect(chunk):
                print("✅ 발화 감지됨 → STT로 전송")
                text = await dispatcher.send_chunk(chunk)
                print("📝 변환 결과:", text)
            else:
                print("❌ 발화 없음 → 무시")

        await asyncio.sleep(0.01)

if __name__ == "__main__":
    asyncio.run(main())
