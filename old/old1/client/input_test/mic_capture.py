import pyaudio
import webrtcvad
import threading
import queue
import time

RATE = 16000
CHANNELS = 1
CHUNK_DURATION_MS = 30
FRAME_SAMPLES = int(RATE * CHUNK_DURATION_MS / 1000)
CHUNK_SIZE = FRAME_SAMPLES * 2

MAX_BUFFER_BYTES = RATE * 3 * 2
MIN_FLUSH_BYTES = int(RATE * 0.6) * 2

class MicCapture:
    def __init__(self):
        self.vad = webrtcvad.Vad(2)
        self.audio_q = queue.Queue()
        self.buffer = bytearray()
        self.running = False
        self.last_voice_time = time.time()

    def start(self):
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _is_speech(self, frame: bytes) -> bool:
        expected_sizes = {int(RATE * 0.01) * 2, int(RATE * 0.02) * 2, int(RATE * 0.03) * 2}
        if len(frame) not in expected_sizes:
            return False
        try:
            return self.vad.is_speech(frame, RATE)
        except Exception:
            return False

    def _capture_loop(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16,
                         channels=CHANNELS,
                         rate=RATE,
                         input=True,
                         frames_per_buffer=FRAME_SAMPLES)

        print("🎙️ 마이크 캡처 시작")

        while self.running:
            frame = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            if self._is_speech(frame):
                self.buffer.extend(frame)
                self.last_voice_time = time.time()
            else:
                if time.time() - self.last_voice_time > 0.6 and len(self.buffer) >= MIN_FLUSH_BYTES:
                    self.audio_q.put(bytes(self.buffer))
                    self.buffer.clear()

            if len(self.buffer) > MAX_BUFFER_BYTES:
                self.audio_q.put(bytes(self.buffer))
                self.buffer.clear()

    def get_audio_chunk(self):
        return self.audio_q.get()
