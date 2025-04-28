FROM python:3.10

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
    edge-tts sounddevice numpy pydub

CMD ["uvicorn", "tester_server:app", "--host", "0.0.0.0", "--port", "8080"]
