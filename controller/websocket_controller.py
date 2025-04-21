from fastapi import APIRouter, WebSocket, WebSocketDisconnect, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import base64

from service_client.stt_client import send_to_stt
from service_client.llm_client import send_to_llm

router = APIRouter()

# 연결된 테스트 수신자 보관
active_testers = []

@router.websocket("/ws")
async def handle_main_stream(websocket: WebSocket):
    await websocket.accept()
    print("[Controller] WebSocket 연결 수락", flush=True)

    try:
        while True:
            raw_msg = await websocket.receive_text()
            msg = json.loads(raw_msg)
            msg_type = msg.get("type")
            payload = msg.get("payload")

            if msg_type == "audio":
                print("[Controller] 🎧 오디오 STT 처리 시작", flush=True)
                stt_text = await send_to_stt(payload)
                print(f"[Controller] 📝 STT 결과: {stt_text}", flush=True)

                llm_response = await send_to_llm(stt_text)
                print(f"[Controller] 💬 LLM 결과: {llm_response}", flush=True)

                for tester_ws in active_testers:
                    await tester_ws.send_text(llm_response)

            elif msg_type == "text":
                print(f"[Controller] ✉️ 텍스트 입력 수신: {payload}", flush=True)
                llm_response = await send_to_llm(payload)
                print(f"[Controller] 💬 LLM 결과: {llm_response}", flush=True)

                for tester_ws in active_testers:
                    await tester_ws.send_text(llm_response)
                    print(f"[Controller] 🧪 테스트 수신자에게 전송 완료", flush=True)


    except WebSocketDisconnect:
        print("[Controller] ❌ 연결 종료", flush=True)


@router.websocket("/ws/test")
async def handle_test_listener(websocket: WebSocket):
    await websocket.accept()
    active_testers.append(websocket)
    print("[Controller] 🧪 테스트 수신자 등록", flush=True)
    try:
        while True:
            await websocket.receive_text()  # 유지용
    except WebSocketDisconnect:
        active_testers.remove(websocket)
        print("[Controller] 🧪 테스트 수신자 제거", flush=True)
