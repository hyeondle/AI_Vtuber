from collections import deque

class AudioBuffer:
    def __init__(self, sample_rate=16000, seconds=3, overlap=1):
        self.sample_rate = sample_rate
        self.chunk_bytes = sample_rate * 2  # 16-bit PCM = 2 bytes
        self.max_bytes = seconds * self.chunk_bytes
        self.overlap_bytes = overlap * self.chunk_bytes

        self.buffer = deque()

    def add_frame(self, frame: bytes):
        self.buffer.append(frame)
        current_size = sum(len(f) for f in self.buffer)
        while current_size > self.max_bytes:
            self.buffer.popleft()
            current_size = sum(len(f) for f in self.buffer)

    def get_chunk(self) -> bytes:
        return b''.join(self.buffer)

    def flush_chunk(self):
        """오버랩 부분만 유지하고 나머지는 삭제"""
        data = self.get_chunk()
        keep = data[-self.overlap_bytes:]
        self.buffer.clear()
        self.buffer.append(keep)
