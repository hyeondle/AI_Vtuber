from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from utils.settings import toggle_gpu, USE_GPU
from utils.transcriber import transcribe_audio

app = FastAPI()

###################
# STT 모델 관련 API #
###################

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        audio_data = await file.read()
        result = transcribe_audio(audio_data, file.filename)
        return JSONResponse(content={"text": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/gpu-toggle")
def toggle_gpu_endpoint():
    new_state = toggle_gpu()
    return {"gpu_enabled": new_state}

@app.get("/")
def index():
    html = """
    <html>
        <body>
            <h2>STT 컨트롤 패널</h2>
            <button onclick="toggle()">Toggle GPU</button>
            <p id="status"></p>
            <script>
            async function toggle() {
                const res = await fetch('/gpu-toggle', {method: 'POST'});
                const data = await res.json();
                document.getElementById('status').innerText =
                  'GPU 상태: ' + (data.gpu_enabled ? '사용 중' : '사용 안 함');
            }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html)


###################
# 컨트롤 패널 관련 API#
###################

app.mount("/panel", StaticFiles(directory="control-panel", html=True), name="control-panel")

@app.get("/")
def main_ui():
    return FileResponse("control-panel/index.html")

@app.get("/gpu-status")
def get_gpu_status():
    return {"gpu_enabled": USE_GPU}

@app.post("/transcribe-test")
def test_transcribe():
    return {"text": "이건 예제 텍스트입니다. 실제 오디오 업로드는 구현 중입니다."}
