from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from utils.transcriber import detect_speech, load_model

app = FastAPI()

@app.on_event("startup")
def preload_model():
    load_model(device="cpu")

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    print("파일 수신됨:", file.filename)
    try:
        detected = detect_speech(audio_bytes, file.filename, device="cpu")
        print("발화 감지 결과:", detected)
        return JSONResponse(content={"speech_detected": detected})
    except Exception as e:
        print("에러 발생:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)
