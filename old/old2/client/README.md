# 클라이언트 모듈 (마이크 입력 및 WebSocket 전송기)

## 📌 개요
이 모듈은 사용자의 마이크 입력을 실시간으로 감지하여, 음성이 감지되면 오디오를 녹음하고 STT 서버로 전송합니다. 서버는 Whisper를 통해 이를 텍스트로 변환하여 응답합니다.

## ✅ 주요 기능
- 마이크 입력 감지 및 자동 녹음
- 음성 종료 감지 기반 전송
- WebSocket을 통한 오디오 전송 및 응답 수신

## 🚀 실행 방법
```bash
python audio_client.py
```

## 📦 요구사항
- Python 3.10+
- `pyaudio`, `websockets`, `numpy`

## 🛠 핡현 계정사항
- 🌟 **비동기 분리 처리**:
  - 오디오 녹음 → 버퍼링 → 전송 과정을 비동기 분리
  - STT 서버 전솰 중에도 다음 음성 감지가 가능하게 설계
  - 예: `asyncio.Queue` + producer-consumer 구조로 확장

