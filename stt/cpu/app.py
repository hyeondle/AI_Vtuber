from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from utils.transcriber import transcribe_audio, model_loaded

app = FastAPI()

@app.on_event("startup")
def preload_model():
    model_loaded(device="cpu")

@app.get("/model-status")
def model_status():
    status = model_loaded(device="cpu", check_only=True)
    return {"model_loaded": status}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    try:
        result = transcribe_audio(audio_bytes, file.filename, device="cpu")
        return JSONResponse(content={"text": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
