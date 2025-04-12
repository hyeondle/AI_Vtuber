from collections import deque
import time

class SlidingBufferManager:
    def __init__(self, sample_rate=16000, buffer_duration=2.0):
        self.sample_rate = sample_rate
        self.buffer_duration = buffer_duration
        self.frame_buffer = deque()  # (timestamp, frame)
        self.max_bytes = int(sample_rate * buffer_duration * 2)  # 2초 worth of 16-bit PCM

    def add_frame(self, frame: bytes):
        now = time.time()
        self.frame_buffer.append((now, frame))
        self.trim_old_frames()

    def trim_old_frames(self):
        """지나치게 오래된 프레임 제거"""
        current_time = time.time()
        while self.frame_buffer and (current_time - self.frame_buffer[0][0] > self.buffer_duration):
            self.frame_buffer.popleft()

    def get_current_buffer(self) -> bytes:
        """지금 시점에서 유효한 2초 버퍼 생성"""
        return b''.join([frame for _, frame in self.frame_buffer])
