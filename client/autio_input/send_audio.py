import asyncio
import websockets
import wave
import pyaudio
import time
import io
import numpy as np
import base64

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.0

class AudioRecorder:
    def __init__(self):
        self.frames = []
        self.last_voice_time = None
        self.recording = False

    def start_stream(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                                      input=True, frames_per_buffer=CHUNK)

    def stop_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def is_voice(self, data):
        amplitude = np.frombuffer(data, dtype=np.int16)
        energy = np.abs(amplitude).mean()
        return energy > SILENCE_THRESHOLD

    def record_audio(self):
        self.frames = []
        self.start_stream()
        print("[🎙️] 녹음 시작", flush=True)

        while True:
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            if self.is_voice(data):
                if not self.recording:
                    print("[🟢] 음성 감지", flush=True)
                    self.recording = True
                self.frames.append(data)
                self.last_voice_time = time.time()
            elif self.recording:
                self.frames.append(data)
                if time.time() - self.last_voice_time > SILENCE_DURATION:
                    print("[🛑] 음성 종료", flush=True)
                    break

        self.stop_stream()
        return b"".join(self.frames)

    def to_wav_bytes(self, pcm):
        buffer = io.BytesIO()
        wf = wave.open(buffer, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(pcm)
        wf.close()
        return buffer.getvalue()

async def send_audio():
    recorder = AudioRecorder()
    raw = recorder.record_audio()
    wav = recorder.to_wav_bytes(raw)
    b64 = base64.b64encode(wav).decode()

    uri = "ws://localhost:8080/ws/"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"type": "audio", "payload": b64}))
        print("[📡] 오디오 전송 완료", flush=True)
