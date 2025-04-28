from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from websocket_connect import init_stt_ws, init_llm_ws, init_tester_ws

active_stt_ws = None
active_llm_ws = None
active_tester_ws = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    global active_stt_ws, active_llm_ws, active_tester_ws
    active_stt_ws = await init_stt_ws()
    active_llm_ws = await init_llm_ws()
    active_tester_ws = await init_tester_ws()
    print("[Controller] 모든 WebSocket 연결 완료", flush=True)

@app.websocket("/ws/")
async def handle_client(ws: WebSocket):
    await ws.accept()
    print("[Controller] 클라이언트 WebSocket 연결", flush=True)

    try:
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)

            if data["type"] == "audio":
                await active_stt_ws.send(json.dumps({"payload": data["payload"]}))
                stt_result = await active_stt_ws.recv()

                await active_llm_ws.send(json.dumps({"text": stt_result}))
                llm_result = await active_llm_ws.recv()

                await active_tester_ws.send(json.dumps({"llm_response": llm_result}))
                tts_audio_b64 = await active_tester_ws.recv()

                await ws.send_text(json.dumps({
                    "input_type": "audio",
                    "input_text": llm_result,
                    "audio_b64": tts_audio_b64
                }, ensure_ascii=False))

                print("[Controller] 🛜 Unity로 오디오 전송 완료", flush=True)

            elif data["type"] == "text":
                await active_llm_ws.send(json.dumps({"text": data["payload"]}))
                llm_result = await active_llm_ws.recv()

                await active_tester_ws.send(json.dumps({"llm_response": llm_result}))
                tts_audio_b64 = await active_tester_ws.recv()

                await ws.send_text(json.dumps({
                    "input_type": "audio",
                    "input_text": llm_result,
                    "audio_b64": tts_audio_b64
                }, ensure_ascii=False))

                print("[Controller] Unity로 오디오 전송 완료", flush=True)

    except WebSocketDisconnect:
        print("[Controller] 클라이언트 연결 종료", flush=True)
