# STT 아키텍쳐

```
├── client/                            # 사용자의 로컬에서 실행되는 허브 (마이크 입력 담당)
│   └── audio_streaming_input/
│       ├── main.py                   # 전체 실행 진입점
│       ├── mic_capture.py            # 실시간 마이크 입력 처리
│       ├── audio_buffer.py           # 3초 + 오버랩 청크 버퍼 관리
│       ├── tiny_detector.py          # stt/tiny 컨테이너로 발화 유무 판별
│       └── stt_dispatcher.py         # 실제 STT 호출 전달자
│
├── stt/
│   ├── cpu/               # Whisper base (정식 인식용)
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── utils/
│   │       └── transcriber.py
│   ├── gpu/               # Whisper base (GPU 인식용)
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── utils/
│   │       └── transcriber.py
│   ├── tiny/                          # 발화 감지 컨테이너
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── utils/
│   │       └── transcriber.py
│   │
│   └── proxy/                         # CPU/GPU 분기용 중계 서버
│       ├── app.py
│       ├── Dockerfile
│       └── requirements.txt
```


## 🧠 각 모듈 설명

### 📌 `client/audio_streaming_input`
- 사용자 마이크로부터 오디오를 받아 일정 청크 단위로 분리
- `tiny_detector.py`: 해당 청크를 stt/tiny에 전송하여 발화 여부 판단
- `stt_dispatcher.py`: 실제 발화인 경우 stt/base로 전달하여 텍스트 변환 수행

### 📌 `stt/base`
- Whisper base 모델 기반의 텍스트 추론
- `/transcribe-chunk` API로 청크 입력을 받아 텍스트 반환
- 고성능을 위한 GPU도 지원 가능 (Docker 설정 필요)

### 📌 `stt/tiny`
- Whisper tiny 모델 기반의 텍스트 유무 판별
- `/detect` API로 청크 입력을 받아 텍스트가 있는지 여부를 반환
- 빠른 응답성과 저비용 처리용으로 설계

### 📌 `stt/proxy`
- GPU/CPU 자동 분기 설정을 위한 중간 API 서버
- `/gpu-toggle`, `/gpu-status`, `/transcribe` 등의 경로로 분기
- 컨트롤 패널과의 연동 담당

---

## ⚙️ docker-compose 연동 고려사항

- 각 서비스는 독립된 컨테이너로 실행되며, Dockerfile과 requirements.txt를 포함
- `stt/base`, `stt/tiny`, `stt/proxy`는 `docker-compose.yml`에서 명시
- client 디렉토리는 로컬에서 실행되므로 Docker 대상 아님

### 🔧 예시:
```yaml
docker-compose.yml
services:
  stt_base:
    build: ./stt/base
    ports:
      - "5002:5000"
  stt_tiny:
    build: ./stt/tiny
    ports:
      - "5004:5000"
  stt_proxy:
    build: ./stt/proxy
    ports:
      - "5001:5000"
```

---

## ✅ 향후 확장 고려
- base 외에 `small`, `medium`, `large` 모델 교체 가능성 고려
- tiny 감지 실패 시 fallback 전략 추가 가능
- 컨테이너간 gRPC 또는 메시지 큐로 고속 통신 확장 가능

---

> 본 문서는 Whisper 기반 STT 시스템의 전체 구조를 체계화하여 관리 및 유지보수, 기능 확장에 용이하도록 정리한 문서입니다.
> 설계 예상도이므로, 본 작성과 다를 가능성이 존재합니다.
