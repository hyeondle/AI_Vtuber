from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()
use_gpu = False  # 기본은 CPU

@app.post("/gpu-toggle")
def toggle_gpu():
    global use_gpu
    use_gpu = not use_gpu
    return {"gpu_enabled": use_gpu}

@app.get("/gpu-status")
def get_gpu_status():
    return {"gpu_enabled": use_gpu}

@app.post("/transcribe")
async def proxy_transcribe(request: Request):
    global use_gpu
    target = "http://stt_gpu:5000/transcribe" if use_gpu else "http://stt_cpu:5000/transcribe"

    async with httpx.AsyncClient() as client:
        body = await request.body()
        headers = dict(request.headers)
        response = await client.post(target, content=body, headers=headers)
        return JSONResponse(content=response.json(), status_code=response.status_code)

@app.get("/stt-cpu-status")
async def stt_cpu_status():
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get("http://stt_cpu:5000/model-status", timeout=5.0)
            return res.json()
    except Exception:
        return {"model_loaded": False, "error": "STT CPU 컨테이너 없음"}

@app.get("/stt-gpu-status")
async def stt_gpu_status():
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get("http://stt_gpu:5000/model-status", timeout=5.0)
            return res.json()
    except Exception:
        return {"model_loaded": False, "error": "STT GPU 컨테이너 없음"}
