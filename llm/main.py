# from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
# from pydantic import BaseModel
# import os
# from dotenv import load_dotenv
# from google import genai
# from google.genai import types

# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     raise RuntimeError("환경 변수 GEMINI_API_KEY가 설정되지 않았습니다.")
# else :
#     print(f"[LLM] 환경 변수 GEMINI_API_KEY: {API_KEY}")

# app = FastAPI()
# client = genai.Client(api_key=API_KEY)
# model = "gemini-2.0-flash"

# class Prompt(BaseModel):
#     prompt: str

# @app.post("/generate")
# async def generate_response(prompt: Prompt):
#     print(f"[LLM] 수신 프롬프트: {prompt.prompt}")
#     try:
#         response = client.models.generate_content_stream(
#             model=model,
#             contents=[prompt.prompt],
            
#         )
#         full_response = "".join([part.text for part in response])
#         print(f"[LLM] 생성된 응답: {full_response}")
#         return {"response": full_response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.websocket("/ws/llm")
# async def llm_websocket(ws: WebSocket):
#     await ws.accept()
#     print("[LLM-WS] WebSocket 연결 수락됨")

#     try:
#         while True:
#             msg = await ws.receive_text()
#             print(f"[LLM-WS] 수신 프롬프트: {msg}")
#             try:
#                 response = client.models.generate_content_stream(
#                     model=model,
#                     contents=[msg],
#                 )
#                 full_response = "".join([part.text for part in response])
#                 print(f"[LLM-WS] 응답: {full_response}")
#                 await ws.send_text(full_response)
#             except Exception as e:
#                 await ws.send_text(f"[ERROR] {e}")

#     except WebSocketDisconnect:
#         print("[LLM-WS] 연결 종료됨")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"

app = FastAPI()

@app.websocket("/ws/llm")
async def llm_ws(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            message = await ws.receive_text()
            payload = json.loads(message)
            prompt = payload.get("text", "")
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
