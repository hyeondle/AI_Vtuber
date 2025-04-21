# 📡 WebSocket 기반 STT 시스템 설계 개선 및 구현 분석 문서

## 📌 현재 STT 시스템의 설계 구조 재정리 (WebSocket 기반)

현재 진행하고자 하는 변경사항은 기존의 **REST API 기반의 STT 호출을 실시간 WebSocket 기반으로 변경**하여, 더욱 낮은 지연(latency)과 효율적인 자원 사용을 목표로 합니다.

기존 설계의 중요한 특징은 다음과 같습니다:

- **마이크 입력 → 청크 생성 (2초 슬라이딩 윈도우 + 1초 중첩)**
- **발화 감지 (Whisper tiny 모델)** → 발화 여부에 따라 필터링
- **텍스트 변환 (Whisper base 모델)** → 발화로 확인된 청크만 변환
- **CPU/GPU 분기처리 (Proxy 기반)** → 자원 활용 효율화
- **실시간 스트리밍 처리 구조** (pseudo-streaming + 문맥 유지)

## 🌐 왜 WebSocket인가?

**기존의 REST API 구조**는 다음과 같은 문제점:
- 매 요청마다 연결 설정 및 해제로 인한 네트워크 오버헤드
- 빈번한 연결 및 해제로 인한 지연 증가
- 실시간 처리의 효율성 저하

**WebSocket 구조**는 다음과 같은 장점:
- 지속적인 양방향 연결 → 빠른 데이터 교환, 낮은 지연
- 연결 유지에 따른 효율성 증가 (TCP 연결 재사용)
- 비동기 처리에 적합 → 슬라이딩 윈도우 처리에 최적

## 🔄 WebSocket 기반 전환 시 고려 사항

| 고려 사항 | 설명 |
|-----------|------|
| 연결 유지 | 한 번 열린 연결을 장기 유지 |
| 청크 전송 | 슬라이딩 윈도우에서 청크 준비 시 즉시 전송 |
| 비동기 구조 | WebSocket 클라이언트/서버 모두 `asyncio` 기반 |
| Prefix 처리 | 이전 결과를 활용한 `initial_prompt` 처리 |
| 예외 처리 | 연결 끊김 시 자동 재연결 로직 필요 |
| nginx 설정 | 프록시 설정을 통한 WebSocket 라우팅 필요 |

## 📌 기능 향상 및 점검 방안

### 1. WebSocket 연결 상태 모니터링
- Prometheus/Grafana 기반 연결 상태 시각화 예정

### 2. 슬라이딩 윈도우 최적화
- 청크 길이와 오버랩 비율 조정 (현재: 2초 + 1초 오버랩)

### 3. Prefix 문맥 유지 최적화
- Redis 기반 prefix 관리 예정

### 4. Tiny 모델 최적화
- 발화 감지를 위한 최소 연산 구조 유지

### 5. GPU 자동 분기 유지
- WebSocket 구조에서도 Proxy 구조 유지 및 `/is_ready` 활용

## 📁 디렉토리 구조 예시

```
ai-vtuber-project/
├── stt/
│   ├── cpu_ws/
│   ├── gpu_ws/
│   ├── tiny_ws/
│   └── proxy/
├── client/
│   └── audio_streaming_input/
│       ├── main.py
│       ├── mic_capture.py
│       ├── audio_buffer.py
│       ├── tiny_detector.py
│       └── stt_dispatcher.py
├── control-panel/
│   ├── conf/nginx.conf
│   └── src/
│       ├── index.html
│       ├── toggle.js
│       └── ws_status.js
```

## 📡 시스템 전체 흐름도

```
마이크 입력 (client)
  └── 슬라이딩 윈도우
       ├── WebSocket 발화 감지기 (tiny_ws)
       │     └── False → 폐기
       │     └── True → STT 전송
       └── WebSocket STT 서버 (cpu_ws/gpu_ws)
               └── prefix + 텍스트 변환 반환
```

## ✅ 최종 구조 선택 이유

| 항목 | 장점 |
|------|------|
| WebSocket | 실시간성, 연결 유지, 낮은 오버헤드 |
| 프록시 유지 | GPU 자동 분기, 확장성 보존 |
| Prefix 전략 | 문맥 일관성 보존 |
| 슬라이딩 버퍼 | 유연한 실시간 처리 |

## 🔮 향후 확장 고려

- 문장 단위 전처리 및 마침표 기준 분절
- LLM 연동 시 이전 대화 컨텍스트 관리
- 클라이언트 UI 상 텍스트 실시간 출력
- Whisper 대체 모델 도입 (Faster Whisper 등)
- TTS/LLM 통합 연동 및 립싱크 출력까지 일관된 처리 흐름

---

> 본 문서는 WebSocket 기반 STT 구조로의 전환 과정과 그에 따른 최적화 전략을 중심으로 실시간 AI 시스템의 성능 향상 및 확장성 확보를 목적으로 작성되었습니다.
