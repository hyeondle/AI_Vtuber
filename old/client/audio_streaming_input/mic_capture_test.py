
import pyaudio
import webrtcvad
import threading
import queue
import time

# === 오디오 기본 설정 ===
RATE = 16000
CHANNELS = 1
CHUNK_DURATION_MS = 30  # 프레임 길이(ms): 10 / 20 / 30만 지원됨
FRAME_SAMPLES = int(RATE * CHUNK_DURATION_MS / 1000)  # 예: 480 samples (30ms)
CHUNK_SIZE = FRAME_SAMPLES  # 16-bit PCM: 2 bytes/sample → 960 bytes

# === 버퍼 관련 설정 ===
MAX_BUFFER_BYTES = RATE * 3 * 2         # 3초 worth
MIN_FLUSH_BYTES = int(RATE * 0.6) * 2   # 최소 0.6초 worth

class VADMicCapture:
    def __init__(self):
        self.vad = webrtcvad.Vad(3)  # aggressiveness: 0~3
        self.audio_q = queue.Queue()
        self.buffer = bytearray()
        self.running = False
        self.last_voice_time = time.time()

    def start(self):
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _is_speech(self, frame: bytes) -> bool:
        expected_sizes = {int(RATE * 0.01) * 2, int(RATE * 0.02) * 2, int(RATE * 0.03) * 2}
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
                         frames_per_buffer=FRAME_SAMPLES)  # ⚠️ 샘플 단위!

        print("🎙️ VAD 마이크 캡처 시작 (짧은 발화 대응)")

        while self.running:
            frame = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            print(f"🎧 [Audio] Captured frame of size: {len(frame)} bytes")

            now = time.time()

            if self._is_speech(frame):
                print("✅ 음성 감지됨 (!)")
                self.buffer.extend(frame)
                self.last_voice_time = now
            else:
                print("… 무음")
                silence_duration = now - self.last_voice_time
                if silence_duration > 0.6 and len(self.buffer) >= MIN_FLUSH_BYTES:
                    print("📤 오디오 청크 전송 (무음 경과 + 최소 길이)")
                    self.audio_q.put(bytes(self.buffer))
                    self.buffer.clear()

            if len(self.buffer) > MAX_BUFFER_BYTES:
                print("📤 오디오 청크 전송 (최대 버퍼 초과)")
                self.audio_q.put(bytes(self.buffer))
                self.buffer.clear()
