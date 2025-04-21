# FROM python:3.10
# WORKDIR /app
# COPY . .
# RUN pip install --no-cache-dir websockets
# CMD ["python", "tester.py"]
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn websockets
CMD ["python", "tester_server.py"]