from mic_capture_test import VADMicCapture
from audio_buffer import AudioBuffer
from tiny_detector import is_speech_detected_from_buffer, convert_to_wav_buffer
from stt_sender import send_chunk_to_stt_from_buffer

STT_API_URL = "http://localhost:5002/transcribe-chunk"

def main():
    mic = VADMicCapture()
    buffer = AudioBuffer()
    mic.start()
    print("🎤 실시간 STT with Tiny 감지 시작")

    previous_text = ""

    while True:
        # 1. 마이크에서 VAD 기반 오디오 청크 수신
        frame = mic.get_audio_chunk()
        buffer.add_frame(frame)
        chunk = buffer.get_chunk()

        print("🧪 발화 감지 중...")

        # 2. 오디오 청크를 WAV 버퍼로 변환
        wav_buffer = convert_to_wav_buffer(chunk)

        # 3. 발화 탐지
        if is_speech_detected_from_buffer(wav_buffer):
            print("✅ 발화 감지됨! STT 전송")

            # 4. 같은 WAV 버퍼를 Whisper에 전달
            new_text = send_chunk_to_stt_from_buffer(wav_buffer, STT_API_URL, previous_text)
            print("📝 변환 결과:", new_text)

            previous_text += " " + new_text

            # 5. 청크 초기화 (오버랩만 유지)
            buffer.flush_chunk()
        else:
            print("❌ 발화 없음 (무시됨)")

if __name__ == "__main__":
    main()