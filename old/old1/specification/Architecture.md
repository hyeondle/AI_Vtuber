# 📐 시스템 아키텍처 설계도

1. 사용자 계층
   - 웹 브라우저 (React, Vue, Svelte 등)
   - 모바일 기기 (모바일 웹)
   - 유니티 클라이언트 (3D 모델 UI)

2. API 게이트웨이 계층
   - FastAPI 또는 Flask 기반 API 서버
   - 각 기능 모듈로 RESTful 요청 라우팅 처리

3. 핵심 기능 서비스 계층 (Docker 컨테이너화)
   - [STT 서비스]
     - Whisper 기반 음성 → 텍스트 변환
     - 실시간/비동기 지원
   - [TTS 서비스]
     - GPT-SoVITS 기반 텍스트 → 음성 합성
     - 감정 표현, 페르소나 일관성 유지
   - [LLM 서비스]
     - GPT-4 turbo 기반 응답 생성
     - 프롬프트 엔지니어링, 파인튜닝 적용
   - [모델 제어 API]
     - 유니티 클라이언트와 립싱크/표정 제어 연동
     - 입력 텍스트에 따른 애니메이션 제어

4. 데이터 계층
   - [Redis]
     - 단기 대화 문맥 관리 (세션 컨텍스트)
     - STT/LLM 실시간 연동
   - [MongoDB]
     - 전체 대화 기록 장기 저장
     - 피드백 수집 및 분석용
     - 재학습용 데이터 보관

5. 운영 및 관리 계층
   - Docker & Docker Compose
     - 각 모듈 컨테이너 관리 및 실행
   - .env 환경 변수 파일
     - API 키, 포트 등 보안 설정 분리
   - Prometheus + Grafana
     - 서비스 헬스체크 및 실시간 모니터링
   - 로깅 시스템
     - 각 서비스 단위 로그 기록 및 수집

---

📦 전체 구조는 Microservice Architecture + RESTful API 설계로 되어 있으며,
모든 구성 요소는 Docker 컨테이너로 격리되어 통합됩니다.


---

## 전체 예상도
```
┌───────────────────────────────────────────────────────────┐
│                           Client                          │
│              Web UI / Mobile / Unity Client               │
└───────────────────────────────────────────────────────────┘
                              │ REST API 요청
                              ▼
┌───────────────────────────────────────────────────────────┐
│                 API Gateway (Flask/FastAPI)               │
└───────────────────────────────────────────────────────────┘
    │              │               │                  │
    ▼              ▼               ▼                  ▼
   STT            TTS             LLM            모델 제어 API
 (Whisper)     (GPT-SoVITS)  (GPT-4 turbo)       (Unity 연동)
    │              │               │                  │
    └──────┬───────┴──────┬────────┘
           ▼              ▼
         Redis         MongoDB
```

[모든 서비스는 Docker 컨테이너화 되어 있으며, docker-compose 또는 Kubernetes로 통합 관리됨]

지원 컴포넌트:
- Prometheus + Grafana → 성능 모니터링
- .env 환경 파일 → 민감 정보 관리
- logging 시스템 (각 모듈)


---

## Real-Time STT 예상도
```
사용자 마이크 입력
     ▼
허브 서버: 3초 간격 청크 생성 + 1초 오버랩
     ▼
    발화 감지 컨테이너 (tiny 모델)
     ├── 텍스트 있음 → 본 STT 컨테이너로 전달 (base 이상 모델)
     └── 텍스트 없음 → 청크 폐기
     ▼
    STT 컨테이너 → 텍스트 변환 반환
```

| 컨테이너       | 설명 |
|----------------|------|
| `hub_server`   | 마이크 입력, 청크 생성, 전송 로직, 발화 판단 흐름 제어 |
| `stt_tiny`     | Whisper tiny 모델. 텍스트 유무만 판단. `/detect` API |
| `stt_base`     | Whisper base 모델. 정식 텍스트 변환 수행. `/transcribe-chunk` API |

---

## 🚀 예상 처리 지연 (Latency)

| 구간 | CPU 예상 시간 | GPU 예상 시간 |
|------|----------------|----------------|
| 녹음 (3초) | 실시간 (3초 중첩) | 동일 |
| tiny 추론 | 200~500ms | 50~150ms |
| base 추론 | 1~2s | 300~700ms |
| 전체 예상 | **~4.5s** | **~3.5s** |

---

# 디렉토리 계층 구조 (업데이트 중)

```
ai-vtuber-project/
├── docker-compose.yml
│
├── control-panel/
│   ├── index.html
│   ├── style.css
│   └── toggle.js
│
├── stt/
│   ├── cpu_ws/               # Whisper base (정식 인식용, WebSocket)
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── utils/
│   │       └── transcriber.py
│   ├── gpu_ws/               # Whisper base (GPU 인식용, WebSocket)
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── utils/
│   │       └── transcriber.py
│   ├── tiny_ws/              # Whisper tiny (발화 감지, WebSocket)
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── utils/
│   │       └── transcriber.py
│   └── proxy/                # CPU/GPU 분기용 중계 서버 (REST)
│       ├── app.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── client/                  # 사용자 로컬 마이크 캡처 클라이언트
│   └── mic_input/
│       ├── main.py
│       ├── mic_capture.py
│       ├── audio_buffer.py
│       ├── ws_streamer.py
│       └── utils/
│           └── audio_utils.py
...

```