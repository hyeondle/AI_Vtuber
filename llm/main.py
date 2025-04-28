from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"

app = FastAPI()

pre_prompt = """you should answer in korean. your maximum sentence will be 4.
you should tell brief and concisely.
questions will be following below.\n
qeustion: 
"""

@app.websocket("/ws/llm")
async def llm_ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            message = await ws.receive_text()
            payload = json.loads(message)
            prompt = pre_prompt + payload.get("text", "")
            print(f"[LLM] 프롬프트 수신: {prompt}", flush=True)
            try:
                stream = client.models.generate_content_stream(
                    model=model,
                    contents=[prompt]
                )
                response = "".join([part.text for part in stream])
            except Exception as e:
                response = f"[ERROR] {e}"
            await ws.send_text(response)
    except WebSocketDisconnect:
        print("[LLM] 연결 해제됨", flush=True)
