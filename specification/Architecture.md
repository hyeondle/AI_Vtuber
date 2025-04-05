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

## 그림 예시
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
│   ├── cpu/
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── utils/
│   │       └── transcriber.py
│   │
│   ├── gpu/
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── utils/
│   │       └── transcriber.py
│
├── stt-proxy/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt

```