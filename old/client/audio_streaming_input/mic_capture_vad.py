import pyaudio
import webrtcvad
import threading
import queue
import time

RATE = 16000
CHANNELS = 1
CHUNK_DURATION_MS = 30
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000) * 2  # 16-bit mono
MAX_BUFFER_BYTES = RATE * 3 * 2  # 3초 worth
MIN_FLUSH_BYTES = RATE * 0.6 * 2  # 최소 0.6초 이상일 때만 전송

class VADMicCapture:
    def __init__(self):
        self.vad = webrtcvad.Vad(1)
        self.audio_q = queue.Queue()
        self.buffer = bytearray()
        self.running = False
        self.last_voice_time = time.time()

    def start(self):
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _is_speech(self, frame: bytes) -> bool:
        expected_sizes = {
            int(RATE * 0.01) * 2,  # 10ms
            int(RATE * 0.02) * 2,  # 20ms
            int(RATE * 0.03) * 2   # 30ms
        }

        actual_size = len(frame)
        if actual_size not in expected_sizes:
            print(f"⚠️ [VAD] frame size {actual_size} bytes is invalid! (expected: {expected_sizes})")
            return False

        try:
            result = self.vad.is_speech(frame, RATE)
            print(f"🔍 [VAD] valid frame {actual_size} bytes → is_speech: {result}")
            return result
        except Exception as e:
            print(f"❌ [VAD] Exception while processing frame: {e}")
            return False


    def get_audio_chunk(self):
        return self.audio_q.get()

    def _capture_loop(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK_SIZE)

        print("🎙️ VAD 마이크 캡처 시작 (짧은 발화 대응)")

        while self.running:
            frame = stream.read(CHUNK_SIZE, exception_on_overflow=False)

            # Debugging: 프레임 바이트 길이 확인
            print(f"🎧 [Audio] Captured frame of size: {len(frame)} bytes")

            now = time.time()

            if self._is_speech(frame):
                print("✅ 음성 감지됨 (!)")
                self.buffer.extend(frame)
                self.last_voice_time = now
            else:
                silence_duration = now - self.last_voice_time
                print("… 무음")

                if silence_duration > 0.6 and len(self.buffer) >= MIN_FLUSH_BYTES:
                    print("📤 오디오 청크 전송 (무음 경과 + 최소 길이)")
                    self.audio_q.put(bytes(self.buffer))
                    self.buffer.clear()

            if len(self.buffer) > MAX_BUFFER_BYTES:
                print("📤 오디오 청크 전송 (최대 버퍼 초과)")
                self.audio_q.put(bytes(self.buffer))
                self.buffer.clear()


    # def _capture_loop(self):
    #     pa = pyaudio.PyAudio()
    #     stream = pa.open(format=pyaudio.paInt16,
    #                     channels=CHANNELS,
    #                     rate=RATE,
    #                     input=True,
    #                     frames_per_buffer=CHUNK_SIZE)

    #     print("🎙️ VAD 마이크 캡처 시작 (짧은 발화 대응)")

    #     while self.running:
    #         frame = stream.read(CHUNK_SIZE, exception_on_overflow=False)
    #         now = time.time()

    #         if self._is_speech(frame):
    #             print("!", end="", flush=True)  # 🎯 여기서 느낌표 출력
    #             self.buffer.extend(frame)
    #             self.last_voice_time = now
    #         else:
    #             silence_duration = now - self.last_voice_time
    #             if silence_duration > 0.6 and len(self.buffer) >= MIN_FLUSH_BYTES:
    #                 self.audio_q.put(bytes(self.buffer))
    #                 self.buffer.clear()

    #         if len(self.buffer) > MAX_BUFFER_BYTES:
    #             self.audio_q.put(bytes(self.buffer))
    #             self.buffer.clear()

    """
    def _capture_loop(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16,
                         channels=CHANNELS,
                         rate=RATE,
                         input=True,
                         frames_per_buffer=CHUNK_SIZE)

        print("🎙️ VAD 마이크 캡처 시작 (짧은 발화 대응)")

        while self.running:
            frame = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            now = time.time()

            if self._is_speech(frame):
                self.buffer.extend(frame)
                self.last_voice_time = now
            else:
                silence_duration = now - self.last_voice_time
                if silence_duration > 0.6 and len(self.buffer) >= MIN_FLUSH_BYTES:
                    self.audio_q.put(bytes(self.buffer))
                    self.buffer.clear()

            if len(self.buffer) > MAX_BUFFER_BYTES:
                self.audio_q.put(bytes(self.buffer))
                self.buffer.clear()
"""