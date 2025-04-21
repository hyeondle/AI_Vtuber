import pyaudio

RATE = 16000
CHUNK = int(RATE * 0.03)  # 30ms

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=RATE,
                 input=True,
                 frames_per_buffer=CHUNK)

print("🎙️ 녹음 중... (Ctrl+C로 중단)")

try:
    while True:
        frame = stream.read(CHUNK)
        print(f"입력 바이트 수: {len(frame)} | 샘플 일부: {frame[:10]}")
except KeyboardInterrupt:
    print("🎤 중단됨")
