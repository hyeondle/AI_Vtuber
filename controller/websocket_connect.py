import asyncio
import websockets

# active_stt_ws = None
# active_llm_ws = None
# active_tester_ws = None

# 추후에 각 컨테이너 주소를 문서와 하고 환경변수로 띄워서 관리하기
# 패키징 방식을 통해 해당 웹소켓을 제대로 받도록 해야함
async def init_stt_ws():
    global active_stt_ws
    while True:
        try:
            # print("[Controller] STT WebSocket 연결 시도 중...", flush=True)
            ws = await websockets.connect("ws://stt:8000/ws/stt")
            # active_stt_ws = ws
            print("✅ STT 연결 완료", flush=True)
            return ws
        except Exception as e:
            # print(f"[Controller] STT 연결 실패: {e}", flush=True)
            await asyncio.sleep(2)

async def init_llm_ws():
    global active_llm_ws
    while True:
        try:
            # print("[Controller] LLM WebSocket 연결 시도 중...", flush=True)
            ws = await websockets.connect("ws://llm:8000/ws/llm")
            # active_llm_ws = ws
            print("✅ LLM 연결 완료", flush=True)
            return ws
        except Exception as e:
            # print(f"[Controller] LLM 연결 실패: {e}", flush=True)
            await asyncio.sleep(2)

async def init_tester_ws():
    global active_tester_ws
    while True:
        try:
            # print("[Controller] 🧪 tester WebSocket 연결 시도...", flush=True)
            ws = await websockets.connect("ws://tester:8080/ws/test")
            # active_tester_ws = ws
            print("✅ tester 연결 완료", flush=True)
            return ws
        except Exception as e:
            # print(f"[Controller] 🧪 tester 연결 실패: {e}", flush=True)
            await asyncio.sleep(5)
