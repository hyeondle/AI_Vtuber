import time
from collections import deque

class SlidingAudioBuffer:
    def __init__(self, sample_rate=16000, buffer_duration=2.0, overlap=1.0):
        self.sample_rate = sample_rate
        self.buffer_duration = buffer_duration
        self.overlap = overlap
        self.frames = deque()
        self.max_duration = buffer_duration
        self.last_flush_time = 0.0

    def add_frame(self, frame: bytes):
        now = time.time()
        self.frames.append((now, frame))
        self._trim_old_frames(now)

    def _trim_old_frames(self, now):
        while self.frames and now - self.frames[0][0] > self.max_duration:
            self.frames.popleft()

    def is_ready(self):
        now = time.time()
        return (now - self.last_flush_time) >= self.overlap

    def get_buffer(self) -> bytes:
        self.last_flush_time = time.time()
        return b''.join([frame for _, frame in self.frames])
