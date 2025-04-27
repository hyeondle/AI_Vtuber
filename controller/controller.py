# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.middleware.cors import CORSMiddleware
# import asyncio
# import json
# # from controller.websocket_connect import active_stt_ws, active_llm_ws, active_tester_ws, init_stt_ws, init_llm_ws, init_tester_ws
# from websocket_connect import init_stt_ws, init_llm_ws, init_tester_ws

# active_stt_ws = None
# active_llm_ws = None
# active_tester_ws = None

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.on_event("startup")
# async def startup():
#     global active_stt_ws, active_llm_ws, active_tester_ws
#     # 아래는 모듈화 성공시 사용
#     # asyncio.create_task(init_stt_ws())
#     # asyncio.create_task(init_llm_ws())
#     # asyncio.create_task(init_tester_ws())
#     active_stt_ws = await init_stt_ws()
#     active_llm_ws = await init_llm_ws()
#     active_tester_ws = await init_tester_ws()
#     print("[Controller] 모든 WebSocket 연결 완료", flush=True)

# # @app.websocket("/ws/")
# # async def handle_client(ws: WebSocket):
# #     await ws.accept()
# #     print("[Controller] 클라이언트 WebSocket 연결 수락", flush=True)
# #     global active_stt_ws, active_llm_ws, active_tester_ws

# #     try:
# #         while True:
# #             msg = await ws.receive_text()
# #             data = json.loads(msg)

# #             print(f"[Controller] 수신 메시지: {data}", flush=True)

# #             if data["type"] == "audio":
# #                 print("[Controller] 🎧 오디오 입력 수신", flush=True)

# #                 if active_stt_ws is None or active_llm_ws is None:
# #                     print("[Controller] ⚠️ STT 또는 LLM 연결이 아직 준비되지 않음", flush=True)
# #                     continue

# #                 # await active_stt_ws.send_text(data["payload"])
# #                 await active_stt_ws.send_to_stt(data["payload"])
# #                 stt_result = await active_stt_ws.recv()
# #                 print(f"[Controller] 📝 STT 결과: {stt_result}", flush=True)

# #                 await active_llm_ws.send_text(stt_result)
# #                 llm_result = await active_llm_ws.recv()
# #                 print(f"[Controller] 💬 LLM 응답: {llm_result}", flush=True)

# #                 await broadcast_to_tester({
# #                     "input_type": "audio",
# #                     "input_text": stt_result,
# #                     "llm_response": llm_result
# #                 })

# #             elif data["type"] == "text":
# #                 print("[Controller] ✉️ 텍스트 입력 수신", flush=True)

# #                 if active_llm_ws is None:
# #                     print("[Controller] ⚠️ LLM 연결이 아직 준비되지 않음", flush=True)
# #                     continue

# #                 await active_llm_ws.send_text(data["payload"])
# #                 llm_result = await active_llm_ws.recv()
# #                 print(f"[Controller] 💬 LLM 응답: {llm_result}", flush=True)

# #                 await broadcast_to_tester({
# #                     "input_type": "text",
# #                     "input_text": data["payload"],
# #                     "llm_response": llm_result
# #                 })

# #     except WebSocketDisconnect:
# #         print("[Controller] 클라이언트 연결 종료", flush=True)

# @app.websocket("/ws/")
# async def handle_client(ws: WebSocket):
#     await ws.accept()
#     print("[Controller] 클라이언트 WebSocket 연결", flush=True)

#     global active_stt_ws, active_llm_ws

#     try:
#         while True:
#             msg = await ws.receive_text()
#             data = json.loads(msg)

#             if data["type"] == "audio":
#                 await active_stt_ws.send(data["payload"])
#                 stt_result = await active_stt_ws.receive_text()

#                 await active_llm_ws.send(stt_result)
#                 llm_result = await active_llm_ws.receive_text()

#                 await broadcast_to_tester({
#                     "input_type": "audio",
#                     "input_text": stt_result,
#                     "llm_response": llm_result
#                 })

#             elif data["type"] == "text":
#                 await active_llm_ws.send(data["payload"])
#                 llm_result = await active_llm_ws.recv()

#                 await broadcast_to_tester({
#                     "input_type": "text",
#                     "input_text": data["payload"],
#                     "llm_response": llm_result
#                 })
#     except WebSocketDisconnect:
#         print("[Controller] 클라이언트 연결 종료", flush=True)


# async def broadcast_to_tester(result_obj: dict):
#     global active_tester_ws
#     if active_tester_ws is None:
#         print("[Controller] tester 연결 없음", flush=True)
#         return
#     try:
#         await active_tester_ws.send(json.dumps(result_obj))
#     except Exception as e:
#         print(f"[Controller] tester 전송 실패: {e}", flush=True)


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


# async def broadcast_to_tester(result_obj: dict):
#     global active_tester_ws
#     if active_tester_ws is None:
#         print("[Controller] tester 연결 없음", flush=True)
#         return
#     try:
#         await active_tester_ws.send(json.dumps(result_obj, ensure_ascii=False))
#         print("[Controller] tester 전송 완료", flush=True)
#     except Exception as e:
#         print(f"[Controller] tester 전송 실패: {e}", flush=True)
