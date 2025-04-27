# FROM python:3.10
# WORKDIR /app
# COPY . .
# RUN pip install --no-cache-dir websockets
# CMD ["python", "tester.py"]
FROM python:3.10

# 시스템 오디오 라이브러리 설치 (sounddevice 때문)
RUN apt-get update && apt-get install -y \
    libasound2-dev \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn websockets httpx python-dotenv \
    edge-tts sounddevice numpy

# FastAPI 서버 실행
CMD ["uvicorn", "tester_server:app", "--host", "0.0.0.0", "--port", "8080"]
