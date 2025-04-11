# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import JSONResponse
# from utils.transcriber import transcribe_audio, model_loaded

# app = FastAPI()

# @app.on_event("startup")
# def preload_model():
#     model_loaded(device="cpu")

# @app.get("/model-status")
# def model_status():
#     status = model_loaded(device="cpu", check_only=True)
#     return {"model_loaded": status}

# @app.post("/transcribe")
# async def transcribe(file: UploadFile = File(...)):
#     audio_bytes = await file.read()
#     try:
#         result = transcribe_audio(audio_bytes, file.filename, device="cpu")
#         return JSONResponse(content={"text": result})
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)

# @app.post("/transcribe-chunk")
# async def transcribe_chunk(file: UploadFile = File(...), initial_prompt: str = ""):
#     audio_bytes = await file.read()
#     try:
#         result = transcribe_audio(audio_bytes, file.filename, device="cpu", prompt=initial_prompt)
#         return JSONResponse(content={"text": result})
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)


# try-except를 래퍼로 감싼 방식. 에러 발생시 위로 변경

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


def handle_transcription(file: UploadFile, is_chunk: bool = False, prompt: str = ""):
    async def wrapper():
        audio_bytes = await file.read()
        try:
            result = transcribe_audio(
                audio_bytes,
                file.filename,
                device="cpu",
                prompt=prompt if is_chunk else ""
            )
            print("Transcription result:", result)
            return JSONResponse(content={"text": result})
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    return wrapper()

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    return await handle_transcription(file)

@app.post("/transcribe-chunk")
async def transcribe_chunk(file: UploadFile = File(...), initial_prompt: str = ""):
    return await handle_transcription(file, is_chunk=True, prompt=initial_prompt)


