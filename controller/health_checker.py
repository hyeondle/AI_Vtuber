import httpx
import asyncio

SERVICES = {
    "stt": "http://stt:8000/is_ready",
    "llm": "http://llm:8000/generate"
}

async def wait_for_all_services(timeout: int = 60):
    start = asyncio.get_event_loop().time()
    while True:
        all_ready = True
        for name, url in SERVICES.items():
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.get(url)
                    if r.status_code != 200:
                        print(f"[WAIT] ❌ {name} 준비 안됨: {r.status_code}", flush=True)
                        all_ready = False
            except Exception as e:
                print(f"[WAIT] 🔄 {name} 확인 실패: {e}", flush=True)
                all_ready = False

        if all_ready:
            print("✅ 모든 서비스 준비 완료", flush=True)
            return True

        if asyncio.get_event_loop().time() - start > timeout:
            raise TimeoutError("❌ 일부 서비스가 제한 시간 내에 준비되지 않았습니다.")

        await asyncio.sleep(2)