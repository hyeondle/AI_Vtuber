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
        self.vad = webrtcvad.Vad(2)
        self.audio_q = queue.Queue()
        self.buffer = bytearray()
        self.running = False
        self.last_voice_time = time.time()

    def start(self):
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _is_speech(self, frame: bytes) -> bool:
        return self.vad.is_speech(frame, RATE)

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

    def get_audio_chunk(self):
        return self.audio_q.get()