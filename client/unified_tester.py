import asyncio
import websockets
import wave
import pyaudio
import time
import io
import numpy as np
import base64
import json

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
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

    def is_voice(self, data):
        amplitude = np.frombuffer(data, dtype=np.int16)
        energy = np.abs(amplitude).mean()
        return energy > SILENCE_THRESHOLD

    def record_once(self):
        self.frames = []
        self.recording = False
        print("[🎙️] 마이크 대기 중...", flush=True)

        while True:
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            if self.is_voice(data):
                if not self.recording:
                    print("[🟢] 음성 감지됨", flush=True)
                    self.recording = True
                self.frames.append(data)
                self.last_voice_time = time.time()
            elif self.recording:
                self.frames.append(data)
                if time.time() - self.last_voice_time > SILENCE_DURATION:
                    print("[🛑] 음성 종료", flush=True)
                    break

        return b"".join(self.frames)

    def to_wav_bytes(self, pcm):
        buffer = io.BytesIO()
        wf = wave.open(buffer, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(pcm)
        wf.close()
        return buffer.getvalue()

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

async def mic_sender(ws):
    recorder = AudioRecorder()
    try:
        while True:
            raw = recorder.record_once()
            wav = recorder.to_wav_bytes(raw)
            b64 = base64.b64encode(wav).decode()
            await ws.send(json.dumps({"type": "audio", "payload": b64}))
            print("[📡] 오디오 전송 완료", flush=True)
    finally:
        recorder.close()

async def chat_sender(ws):
    print("✉️ 채팅 입력 모드 (exit 입력 시 종료)", flush=True)
    while True:
        text = input(">> ")
        if text.lower() in ("exit", "quit"):
            break
        await ws.send(json.dumps({"type": "text", "payload": text}))
        print("[📨] 텍스트 전송 완료", flush=True)

async def main():
    uri = "ws://localhost/ws/"
    try:
        async with websockets.connect(uri) as ws:
            print("✅ WebSocket 연결 완료", flush=True)
            await asyncio.gather(
                # mic_sender(ws),
                chat_sender(ws),
            )
    except Exception as e:
        print(f"❌ WebSocket 연결 실패: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
