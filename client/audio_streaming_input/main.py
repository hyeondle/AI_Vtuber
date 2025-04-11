from mic_capture_test import VADMicCapture
from audio_buffer import AudioBuffer
from tiny_detector import is_speech_detected
from stt_sender import send_chunk_to_stt

STT_API_URL = "http://localhost:5002/transcribe-chunk"

def main():
    mic = VADMicCapture()
    buffer = AudioBuffer()
    mic.start()
    print("🎤 실시간 STT with Tiny 감지 시작")

    previous_text = ""

    while True:
        frame = mic.get_audio_chunk()
        buffer.add_frame(frame)
        chunk = buffer.get_chunk()

        print("🧪 발화 감지 중...")

        if is_speech_detected(chunk):
            print("✅ 발화 감지됨! STT 전송")
            new_text = send_chunk_to_stt(chunk, STT_API_URL, previous_text)
            print("📝 변환 결과:", new_text)
            previous_text += " " + new_text
            buffer.flush_chunk()
        else:
            print("❌ 발화 없음 (무시됨)")


if __name__ == "__main__":
    main()
