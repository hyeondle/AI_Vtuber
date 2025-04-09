from mic_capture_vad import VADMicCapture
from stt_sender import send_chunk_to_stt

STT_API_URL = "http://localhost:5002/transcribe-chunk"

def main():
    mic = VADMicCapture()
    mic.start()
    print("🧠 STT 스트리밍 시작 (prefix 유지)")

    previous_text = ""

    while True:
        chunk = mic.get_audio_chunk()
        print("🗣️ 발화 감지됨, Whisper로 전송 중...")
        new_text = send_chunk_to_stt(chunk, STT_API_URL, previous_text)
        if new_text:
            print("📝 변환 결과:", new_text)
            previous_text += " " + new_text

if __name__ == "__main__":
    main()
