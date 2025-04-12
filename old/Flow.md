# 🧠 AI Vtuber 실시간 음성 대화 시스템 전체 흐름

---

## 🎬 시스템 개요

이 문서는 사용자로부터 입력된 음성이 실시간으로 인식되고, 시스템 내부를 거쳐 텍스트로 변환된 후 최종적으로 다시 사용자에게 반환되는 **End-to-End AI Vtuber 대화 흐름**을 설명합니다.

---

## 🧑 사용자 → 🎧 음성 입력

1. 사용자는 마이크를 통해 음성을 말합니다.
2. `client/audio_streaming_input`의 허브 프로그램(`main.py`)이 마이크 입력을 실시간 캡처합니다.
3. `webrtcvad`로 무음 여부를 판단하고, **음성 감지 시** 오디오를 버퍼에 저장합니다.
4. 오디오가 3초(오버랩 1초 포함) 분량이 되면 **청크(chunk)** 로 정의합니다.

---

## 🔍 발화 감지: stt/tiny 컨테이너

5. 생성된 청크는 **`stt/tiny` Whisper tiny 모델 컨테이너**로 전송됩니다.
6. 텍스트가 생성되면 `True` 반환 → 발화 감지  
   텍스트가 없으면 `False` 반환 → 청크 폐기

---

## 🧠 텍스트 변환: stt/cpu or stt/gpu

7. 발화 감지된 청크는 `stt/cpu` 또는 `stt/gpu` 컨테이너로 전송됩니다.
8. 이전 텍스트는 `initial_prompt`로 포함 → **문맥 유지**
9. Whisper base 모델을 사용해 텍스트로 변환합니다.
10. 결과 텍스트를 허브에 반환합니다.

---

## 🧠 이후 처리 흐름 (확장 예정)

11. 텍스트는 **LLM 컨테이너(GPT-4 등)** 에서 자연어 응답 생성
12. 생성된 응답은 **TTS 컨테이너**에서 음성으로 변환
13. 유니티 모델 제어 API로 전달 → 립싱크, 표정 등 제어

---

## 📋 컨트롤 패널

- GPU 사용 ON/OFF
- STT CPU/GPU 상태 확인
- 예제 테스트 실행
- 상태 실시간 확인 가능 (웹 브라우저)

---

## ⚙️ 도커 기반 컨테이너 구조

| 컨테이너 | 역할 |
|----------|------|
| `stt_proxy` | GPU/CPU 분기 |
| `stt_cpu` / `stt_gpu` | Whisper base 모델 |
| `stt_tiny` | Whisper tiny 발화 감지 |
| `control_panel` | 상태 UI |
| `client` | 로컬 허브 프로그램 |

---

## 🧩 전체 구조 요약 다이어그램

```
🎤 사용자 발화
   ↓
client/audio_streaming_input/main.py
   ↓ (3초 청크 생성)
stt/tiny (발화 감지)
   ↓ (True인 경우)
stt/cpu or stt/gpu (텍스트 변환)
   ↓
client에서 출력 (or LLM → TTS → Unity로 확장)
```

---

## ✅ 핵심 기술 요약

| 기술 요소 | 적용 내용 |
|-----------|-----------|
| Whisper | STT 및 tiny 모델 |
| VAD | 무음 판단 |
| FastAPI | 모든 API 서버 |
| Docker | 컨테이너 관리 |
| PyAudio | 마이크 입력 |
| WebSocket/REST | 통신 |
| nginx | UI 호스팅 |
| Prometheus (예정) | 성능 모니터링 |

