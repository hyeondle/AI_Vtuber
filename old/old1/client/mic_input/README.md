# 🎧 Client Audio Streaming System Documentation

## ✅ 개요
이 문서는 클라이언트 측에서 마이크 입력을 통해 실시간 오디오 스트리밍을 처리하고, Whisper 기반의 STT 서버와 WebSocket을 통해 상호작용하는 전체 동작 흐름과 각 모듈에 대한 설명을 정리합니다.

---

## 📦 디렉토리 구조

```
client/
└── audio_streaming_input/
    ├── main.py                 # 실행 진입점
    ├── mic_capture.py          # 마이크 입력 처리
    ├── audio_buffer.py         # 슬라이딩 버퍼 (2초 + 1초 오버랩)
    ├── tiny_detector_ws.py     # 발화 감지용 WebSocket 클라이언트
    └── stt_dispatcher_ws.py    # STT 처리용 WebSocket 클라이언트
```

---

## 🔁 전체 동작 흐름

1. `main.py`에서 `MicCapture` 클래스를 통해 마이크 입력 스트림 시작
2. 매 프레임(30ms) 단위로 오디오 데이터를 받아 `SlidingAudioBuffer`에 추가
3. 슬라이딩 버퍼가 2초 이상 구성되면 청크 추출
4. `TinySpeechDetector`를 통해 해당 청크에 발화가 있는지 WebSocket으로 감지 요청
5. 발화가 감지되면, `STTDispatcher`를 통해 청크 데이터를 Whisper STT 서버에 전송
6. 변환된 텍스트를 콘솔에 출력

---

## 🔧 모듈별 설명

### `mic_capture.py`
- `MicCapture` 클래스는 PyAudio와 WebRTC VAD를 사용하여 마이크 입력을 지속적으로 수신합니다.
- 감지된 음성 프레임을 내부 버퍼에 저장하며, 무음 상태가 0.6초 이상 지속되면 버퍼를 `audio_q`에 전달합니다.

### `audio_buffer.py`
- `SlidingAudioBuffer` 클래스는 2초 분량의 오디오를 수집하며, 1초씩 오버랩되도록 구성합니다.
- 청크 구성 완료 시, `.get_buffer()`로 현재 버퍼를 반환하고 오버랩 구간을 유지하며 앞부분을 삭제합니다.

### `tiny_detector_ws.py`
- `TinySpeechDetector` 클래스는 WebSocket으로 연결하여 오디오 청크를 서버에 전송하고, 텍스트 유무로 발화를 감지합니다.
- Whisper Tiny 모델을 사용하는 서버에서 `/ws/detect` WebSocket 엔드포인트를 통해 감지 요청을 처리합니다.

### `stt_dispatcher_ws.py`
- `STTDispatcher` 클래스는 발화가 감지된 오디오 청크를 Whisper Base 모델이 로드된 STT 서버에 전송합니다.
- `/ws/transcribe` WebSocket 엔드포인트를 통해 음성 텍스트 변환을 요청합니다.

### `main.py`
- 모든 모듈을 연결하여 동작시키는 진입점입니다.
- `asyncio` 기반의 이벤트 루프에서 마이크 → 버퍼링 → 감지 → 전송 과정을 비동기로 처리합니다.

---

## ⚙️ 주요 파라미터

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `BUFFER_DURATION` | 슬라이딩 버퍼 길이 (초) | `2.0` |
| `OVERLAP_DURATION` | 버퍼 오버랩 길이 (초) | `1.0` |
| `CHUNK_DURATION_MS` | 프레임 길이 (ms) | `30` |
| `RATE` | 샘플링 레이트 | `16000 Hz` |
| `CHANNELS` | 채널 수 | `1 (Mono)` |

---

## 📌 기대 효과
- 무의미한 무음 구간 전송 방지 → 성능 향상
- 청크 기반 비동기 처리로 자연스러운 스트리밍 효과
- Whisper Tiny → Whisper Base 연계로 정확도와 속도 균형 유지

---

> 본 시스템은 WebSocket 기반 실시간 STT 시스템의 핵심 구조를 클라이언트에서 구현한 것으로, 추후 TTS/LLM/애니메이션 동기화에 활용될 수 있습니다.

