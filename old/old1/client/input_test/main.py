import asyncio
from mic_capture import MicCapture
from ws_client import STTWebSocketClient

TINY_WS_URL = "ws://localhost:5004/ws/detect"
STT_WS_URL = "ws://localhost:5002/ws/transcribe"

async def main():
    mic = MicCapture()
    mic.start()

    tiny_client = STTWebSocketClient(TINY_WS_URL)
    stt_client = STTWebSocketClient(STT_WS_URL)
    await tiny_client.connect()
    await stt_client.connect()

    print("🎧 WebSocket 연결 완료. STT 스트리밍 시작.")

    while True:
        chunk = mic.get_audio_chunk()
        print("🔎 발화 감지 중...")
        result = await tiny_client.send_audio(chunk)

        if '"speech_detected": true' in result:
            print("✅ 발화 감지됨 → STT로 전송")
            text = await stt_client.send_audio(chunk)
            print("📝 텍스트:", text)
        else:
            print("❌ 무시됨")

if __name__ == "__main__":
    asyncio.run(main())
