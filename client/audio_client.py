import pyaudio
import wave
import websockets
import asyncio
import time
import threading
from collections import deque
import io
import numpy as np

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
SILENCE_THRESHOLD = 500  # 단순 에너지 기준
SILENCE_DURATION = 1.0   # 초

class AudioRecorder:
    def __init__(self):
        self.frames = []
        self.recording = False
        self.last_voice_time = None
        self.stream = None
        self.audio = None  # 지연 생성

    def find_input_device(self):
        for i in range(pyaudio.PyAudio().get_device_count()):
            info = pyaudio.PyAudio().get_device_info_by_index(i)
            if info.get('maxInputChannels') > 0:
                print(f"🎧 입력 장치 사용: {info['name']} (index: {i})")
                return i
        raise RuntimeError("🎤 입력 가능한 오디오 장치가 없습니다")

    def start_stream(self):
        self.audio = pyaudio.PyAudio()
        device_index = self.find_input_device()
        self.stream = self.audio.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      frames_per_buffer=CHUNK,
                                      input_device_index=device_index)

    def stop_stream(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio is not None:
            self.audio.terminate()
            self.audio = None

    def is_voice(self, data):
        amplitude = np.frombuffer(data, dtype=np.int16)
        energy = np.abs(amplitude).mean()
        return energy > SILENCE_THRESHOLD

    def record_audio(self):
        print("🎙️ 마이크 녹음 시작...")
        self.start_stream()
        self.frames = []
        self.recording = False

        while True:
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            if self.is_voice(data):
                if not self.recording:
                    print("🟢 음성 감지 시작")
                    self.recording = True
                self.frames.append(data)
                self.last_voice_time = time.time()
            elif self.recording:
                self.frames.append(data)
                if time.time() - self.last_voice_time > SILENCE_DURATION:
                    print("🛑 음성 종료 감지")
                    break

        self.stop_stream()
        return self.frames

    def frames_to_wav(self, frames):
        buffer = io.BytesIO()
        wf = wave.open(buffer, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return buffer.getvalue()




async def send_audio():
    recorder = AudioRecorder()
    frames = recorder.record_audio()
    audio_bytes = recorder.frames_to_wav(frames)

    async with websockets.connect("ws://localhost:8001/ws/stt") as websocket:
        print("📡 STT 서버에 오디오 전송 중...")
        await websocket.send(audio_bytes)
        result = await websocket.recv()
        print(f"📝 STT 결과: {result}")

async def run_client():
    recorder = AudioRecorder()
    uri = "ws://localhost:8080/ws/stt"  # nginx를 통해 프록시할 경우

    async with websockets.connect(uri) as websocket:
        print("✅ STT 서버와 WebSocket 연결 완료")

        while True:
            frames = recorder.record_audio()
            audio_bytes = recorder.frames_to_wav(frames)

            print("📡 STT 서버에 오디오 전송 중...")
            await websocket.send(audio_bytes)
            result = await websocket.recv()
            print(f"📝 STT 결과: {result}")

if __name__ == "__main__":
    asyncio.run(run_client())
