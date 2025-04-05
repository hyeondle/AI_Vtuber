import requests

# 테스트용 오디오 파일 경로 (확장자 자유: .wav, .mp3, .m4a 등)
file_path = "test_audio/sample.m4a"

# 파일 업로드
files = {"file": open(file_path, "rb")}
res = requests.post("http://localhost:5002/transcribe", files=files)

# 결과 출력
if res.ok:
    print("🗣️ Transcription Result:", res.json()["text"])
else:
    print("❌ Error:", res.status_code, res.text)
