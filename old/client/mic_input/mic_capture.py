import pyaudio
import webrtcvad
import threading
import queue
import time

RATE = 16000
CHANNELS = 1
CHUNK_DURATION_MS = 30
FRAME_SAMPLES = int(RATE * CHUNK_DURATION_MS / 1000)
CHUNK_SIZE = FRAME_SAMPLES * 2  # 16-bit PCM

class MicCapture:
    def __init__(self, aggressiveness: int = 2):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.audio_q = queue.Queue()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _is_speech(self, frame: bytes) -> bool:
        if len(frame) not in {int(RATE * 0.01) * 2, int(RATE * 0.02) * 2, int(RATE * 0.03) * 2}:
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

        print("🎙️ 마이크 입력 캡처 시작")

        while self.running:
            frame = stream.read(FRAME_SAMPLES, exception_on_overflow=False)
            if self._is_speech(frame):
                self.audio_q.put(frame)

    def get_audio_chunk(self) -> bytes:
        return self.audio_q.get()
