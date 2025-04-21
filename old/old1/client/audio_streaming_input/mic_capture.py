"""
해당 파일은 VAD가 적용되지 않아
모든 발화가 마무리 된 이후에
오디오를 전체 전송하므로, 실시간 방식에 맞지 않아
테스트용도로 남겨둔 파일입니다.
"""

import pyaudio
import threading
import queue

CHUNK_DURATION_SEC = 3  # 청크 길이 (초)
RATE = 16000
CHUNK_SIZE = RATE * CHUNK_DURATION_SEC  # 샘플 수
CHANNELS = 1
FORMAT = pyaudio.paInt16

class MicCapture:
    def __init__(self):
        self.audio_q = queue.Queue()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _capture_loop(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=FORMAT,
                         channels=CHANNELS,
                         rate=RATE,
                         input=True,
                         frames_per_buffer=CHUNK_SIZE)
        print("🎙️ 마이크 캡처 시작")
        while self.running:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            self.audio_q.put(data)

    def get_audio_chunk(self):
        return self.audio_q.get()
