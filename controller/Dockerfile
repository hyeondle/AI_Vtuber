FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn websockets httpx python-dotenv requests
CMD ["uvicorn", "controller:app", "--host", "0.0.0.0", "--port", "8080"]