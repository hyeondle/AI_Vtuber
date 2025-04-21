import httpx

STT_WS_URL = "ws://stt:8000/ws/stt"

async def send_to_stt(audio_b64: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            ws = await client.ws_connect(STT_WS_URL)
            await ws.send_text(audio_b64)
            msg = await ws.receive_text()
            await ws.aclose()
            return msg
        except Exception as e:
            print(f"[STT Client] 오류: {e}", flush=True)
            return "[ERROR] STT 오류"