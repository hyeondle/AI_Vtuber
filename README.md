# 🧠 AI VTuber WebSocket System

이 프로젝트는 마이크 입력과 채팅 입력을 기반으로 실시간 STT → LLM → TTS 흐름을 처리하는 **모듈형 AI VTuber 시스템**입니다. 모든 통신은 WebSocket을 기반으로 하며, STT/LLM/TTS 모듈은 독립된 컨테이너로 구동됩니다.

---

## 🏗️ 전체 구조

```
                 [🎙️ Mic / Chat Input]
                           ↓
               ┌──────────────────────┐
               │      controller       │◀── tester (output log / TTS 예정)
               └──────────────────────┘
                  │       │        ▲
        (audio)   ▼       ▼        │ (json broadcast)
              [stt]    [llm]     ───┘
           (base64)   (prompt)
```


---

## 🔌 구성 요소

### 1. `controller` (FastAPI)
- 클라이언트로부터 WebSocket 메시지를 수신
- STT 서버에 base64 오디오 전송
- LLM 서버에 텍스트 프롬프트 전달
- Tester에 최종 결과 broadcast

### 2. `stt` (Faster-Whisper)
- base64 WAV 오디오를 받아서 Whisper 모델로 텍스트 추출
- 결과를 WebSocket을 통해 반환

### 3. `llm` (Gemini 2.0 Flash)
- 텍스트 입력을 받아 Gemini API로 응답 생성
- 생성된 응답을 WebSocket으로 반환

### 4. `tester`
- WebSocket을 통해 controller가 broadcast한 최종 메시지를 수신
- 콘솔 출력 (추후 TTS 연결 예정)

### 5. `client/unified_tester.py`
- 마이크 음성 감지 후 자동 전송 (SILENCE_THRESHOLD 기반)
- 키보드 입력으로 채팅 전송
- WebSocket으로 controller에 접속

---

## ⚙️ 실행 방법

```bash
# 도커 실행
$ docker-compose up --build

# 로컬에서 unified_tester 실행 (마이크/채팅 클라이언트)
$ python3 client/unified_tester.py
```

---

## 🌐 WebSocket 포트 및 경로

| 역할 | 경로 | 설명 |
|------|------|------|
| Controller (수신) | `ws://localhost/ws/` | 마이크/채팅 통합 수신 |
| Controller → STT | `ws://stt:8000/ws/stt` | base64 오디오 전송 |
| Controller → LLM | `ws://llm:8000/ws/llm` | 텍스트 프롬프트 전송 |
| Controller → Tester | `ws://tester:8080/ws/test` | 최종 결과 전송 |

---

## 🧠 아키텍처 설계 특징

- FastAPI 기반 WebSocket 서버: STT, LLM, Tester는 모두 독립 서버
- Python `websockets` 클라이언트: controller가 모든 서버에 연결하는 허브
- 음성 감지 + 마이크 상시 대기 (PyAudio)

---

## 🛣️ 향후 계획

- 🗣️ TTS(Talk) 컨테이너 도입
- 🎭 캐릭터 제스처와 연동되는 Avatar 모듈 개발
- 💾 Database/Memory 기반 Context 유지
