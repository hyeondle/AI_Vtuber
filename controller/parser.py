import json
import re

def parse_response(response_text: str) -> dict:
    try:
        # ```json ... ``` 블록에서 내부 JSON 추출
        match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if match:
            raw_json = match.group(1)
        else:
            raw_json = response_text.strip()

        parsed = json.loads(raw_json)

        # 예시 필드 추출
        result = {
            "llm_text": parsed["llm"]["response"],
            "tts_emotion": parsed["tts"]["emotion"],
            "tts_speed": parsed["tts"]["speed"],
            "tts_pitch": parsed["tts"]["pitch"],
            "unity_emotion": parsed["unity"]["emotion"],
            "unity_situation": parsed["unity"]["situation"],
            "unity_action": parsed["unity"]["action"]
        }

        return result

    except Exception as e:
        print(f"[Parser] ❌ JSON 파싱 실패: {e}")
        return {
            "llm_text": "[ERROR] LLM 응답 파싱 실패",
            "tts_emotion": {},
            "tts_speed": 1.0,
            "tts_pitch": 1.0,
            "unity_emotion": {},
            "unity_situation": "neutral",
            "unity_action": "idle"
        }
