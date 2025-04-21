# STT 모듈 - Whisper 기반 음성 인식 서비스

## 개요
이 모듈은 실시간 WebSocket 기반으로 클라이언트에서 전송된 단일 음성 버퍼를 받아 Whisper를 통해 텍스트로 변환하는 기능을 수행합니다. 해당 STT 서버는 단일 음성 구간(예: 발화 시작부터 끝까지)을 하나의 버퍼로 처리하는 단순화된 구조를 채택하여 빠르고 직관적인 음성 인식 처리를 목표로 합니다.

---

## 기능 설명

### 🔊 오디오 입력 처리
- 마이크에서 실시간으로 감지된 음성을 하나의 `.wav` 버퍼로 생성
- 음성 시작-끝이 명확하다는 전제 하에, 별도의 VAD는 사용하지 않음

### 🌐 WebSocket 서버
- 클라이언트가 WebSocket으로 음성 버퍼를 전송
- 서버는 음성을 Whisper로 처리하여 텍스트 응답 반환

### 🧠 Whisper STT 엔진
- faster-whisper를 사용하여 빠른 추론 지원
- GPU/CPU 동작 선택 가능

## ✅ 주요 기능
- `faster-whisper` 기반 음성 인식
- FastAPI 기반 WebSocket 서버
- Docker 컨테이너화
- 모델은 서버 시작 시 메모리에 1회만 로딩
- `/is_ready` 엔드포인트로 헬스체크 가능


---

## 시스템 구성도

```plaintext
[🎙️ Mic Input] → [🎧 Buffering] → [📡 WebSocket 송신] → [🧠 STT 처리] → [📜 텍스트 응답]


