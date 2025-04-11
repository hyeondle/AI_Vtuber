# 🧏 Whisper 기반 STT 시스템 통합 설계 및 분석 문서

이 문서는 Whisper를 기반으로 한 STT(Speech-to-Text) 시스템을 다음과 같은 항목에 따라 완전하게 기술합니다:

1. 전체 디렉토리 구조 및 구성 요소
2. 실시간 처리 전략 및 청크 구조
3. CPU/GPU 이중 컨테이너 구성 (`stt/cpu`, `stt/gpu`)
4. 발화 감지를 위한 `stt/tiny` 컨테이너
5. STT 프록시 라우터 `stt/proxy`
6. 마이크 입력 및 클라이언트 스트리밍 구성 (`client/audio_streaming_input`)
7. 선택한 구조의 기술적 정당성과 전략

---

## 📦 전체 디렉토리 구성

```
ai-vtuber-project/
├── stt/
│   ├── cpu/                  # Whisper base (CPU)
│   ├── gpu/                  # Whisper base (GPU)
│   ├── tiny/                 # Whisper tiny (발화 감지)
│   └── proxy/                # CPU/GPU 중계 (FastAPI 기반)
│
├── client/
│   └── audio_streaming_input/
│       ├── mic_capture.py
│       ├── audio_buffer.py
│       ├── tiny_detector.py
│       ├── stt_dispatcher.py
│       └── main.py
```

---

## ⚙️ 실시간 처리 흐름 요약

1. `client/audio_streaming_input/main.py` 시작 → 마이크 입력 수신
2. 3초 단위 + 1초 오버랩 → 청크 생성
3. `stt/tiny`의 `/detect` API로 전송 → 발화 여부 판단
4. 발화 발생 시 `stt/proxy`의 `/transcribe` API로 전달
5. 프록시는 GPU 활성화 여부 확인 → `stt/cpu` or `stt/gpu` 선택하여 `/transcribe-chunk` 호출
6. 결과 텍스트 반환

---

## 🧪 실시간 처리 전략 비교

### ✅ 전략 1: 단일 STT 컨테이너 (base 모델 하나로 모든 청크 처리)
- 처리 단순화, 컨테이너 하나만 관리
- 무의미한 청크까지 모두 처리 → 비효율
- 발화가 아닌 청크에서도 문맥 꼬임 발생 가능
- 정확도 유지 어려움, 속도 병목 발생 가능

### ✅ 전략 2: `stt/tiny`를 이용한 이중 구조 (Tiny + Base 모델)
- 작은 모델로 선별 후 중요한 청크만 정식 처리
- 오버헤드 줄이고 GPU 활용 최적화
- 발화 감지를 Whisper로 직접 처리 → 정확도 높음
- 약간의 구조 복잡도 증가 (API 설계 필요)

---

## 🔁 CPU vs GPU 처리 비교

| 항목 | CPU 예상 | GPU 예상 |
|------|----------|----------|
| Tiny 감지 | 200~500ms | 50~150ms |
| Base 변환 | 1~2s | 300~700ms |
| 전체 지연 | 약 4.5s | 약 3.5s |

- GPU의 경우 대화 흐름 지연 없이 빠른 반응 가능
- CPU는 응답 시간은 수용 가능하지만 동시 요청에 병목 가능성 있음

---

## 🧭 선택된 최종 구조: 프록시 기반 이중 컨테이너 + 발화 감지 구조

### 🧠 선택 이유

- **실시간성**: 불필요한 청크 제거로 평균 응답 시간을 줄임
- **정확도**: Tiny 모델로 발화 여부 감지 후 Base 모델로 문맥 중심 변환
- **확장성**: CPU/GPU 자동 분기 구조로 다양한 디바이스에 대응 가능
- **유지보수성**: 모든 구성 요소가 컨테이너화 되어 관리 용이
- **유연성**: 컨트롤 패널을 통해 GPU 사용 토글 가능

---

## 🧩 장점 vs 단점 비교

| 항목 | 장점 | 단점 |
|------|------|------|
| `stt/tiny` | 빠른 감지, 정확한 발화 분리 | 추가 컨테이너 유지 필요 |
| `stt/proxy` | 구조 분리, GPU 자동 분기 | 상태 동기화 필요 |
| `stt/cpu + gpu` | 확장성, 성능 확보 | 리소스 사용 ↑ |
| 전체 구조 | 유연, 고정확도, 실시간성 우수 | 다소 복잡한 구성 |

---

## 🔮 향후 확장 고려

- LLM 연동 시 prefix 재구성 및 문장 경계 명확화
- TTS 호출 및 애니메이션 동기화까지 연계 가능
- Redis 캐시를 통한 이전 텍스트 관리
- WebSocket 서버 통합 (hub_server 완성 후)

---
