from google import genai
from google.genai import types

API_KEY = "AIzaSyDLihX3envEQq7Ja_HOcvlgJTvZFHUP75k"
client = genai.Client(api_key=API_KEY)
model = "gemini-2.0-flash"


response = client.models.generate_content_stream(
    model=model,
    # contents=prompt.message,
    contents=["explain how to calculate the area of a circle"],
    config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=500,
        system_instruction="All the responses should be Korean",
    )
    
)

for chunk in response:
    print(chunk.text, end="", flush=True)

