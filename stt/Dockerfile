FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn faster-whisper websockets
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]