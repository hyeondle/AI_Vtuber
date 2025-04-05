from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from utils.transcriber import transcribe_audio

app = FastAPI()

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    try:
        result = transcribe_audio(audio_bytes, file.filename, device="cpu")
        return JSONResponse(content={"text": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
