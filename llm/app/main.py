from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import os
from dotenv import load_dotenv

from google import genai
from google.genai import types

# Load env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("환경 변수 GEMINI_API_KEY가 설정되지 않았습니다.")

app = FastAPI()

# Gemini Setting
client = genai.Client(api_key=API_KEY)
model = "gemini-2.0-flash"

# 히스토리 로드 및 컨텍스트 처리 추가 필요

# 일단은 prompt로 받고, 대답을 생성하는 api만 구현.
@app.post("/generate")
async def generate_response(prompt):
    try:
        response = client.models.generate_content_stream(
            model=model,
            # contents=prompt.message,
            contents=["explain how to calculate the area of a circle"],
        )
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 생성된 응답을 전송하거나 데이터베이스에 저장하고 처리하는 함수 구현 필요
# 답변의 형태는 정규식으로 분리가 가능하도록 유도해야함
