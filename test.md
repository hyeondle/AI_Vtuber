# AI VTuber 실시간 STT-LLM 처리 구조 기반 WebSocket 모듈화 설계

# 🔧 디렉토리 구조
#
# client/
# ├── audio_input/            → 마이크 입력을 받아 오디오 데이터를 WebSocket으로 전송
# ├── text_input/             → 키보드 텍스트를 WebSocket으로 전송
# controller/
# ├── websocket_controller.py → 전체 흐름 관리, 메시지 라우팅
# ├── health_checker.py      → 컨테이너 준비 상태 확인 후 WebSocket 수락
# service_client/
# ├── stt_client.py          → STT 컨테이너 호출
# ├── llm_client.py          → LLM 컨테이너 호출
# stt/
# ├── main.py                → Whisper 모델 STT WebSocket 서버
# ├── whisper_utils.py       → 모델 로드 및 오디오 텍스트 변환 함수
# └── Dockerfile             → STT 컨테이너 정의
# llm/
# ├── main.py                → Gemini API 기반 FastAPI 서버
# └── Dockerfile             → LLM 컨테이너 정의
# controller/
# ├── websocket_controller.py
# ├── health_checker.py
# └── Dockerfile             → 컨트롤러 서버 정의
# test/
# ├── tester.py
# └── Dockerfile             → 테스트 수신 컨테이너 정의
# nginx/
# ├── nginx.conf             → WebSocket 프록시 설정
# └── Dockerfile             → Nginx 웹 프록시 서버 정의
# docker-compose.yml         → 전체 서비스 오케스트레이션 구성