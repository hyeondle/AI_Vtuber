# 🔁 향후 고려 (현재 코드 한계)

- Whisper는 load_model()로 모델을 미리 불러오는 구조이기 때문에, 컨트롤 패널에서 toggle해도 런타임 중에는 적용이 안 됨
- 이를 해결하려면:
    - 모델을 요청마다 새로 로드하거나
    - GPU 전용 서버와 CPU 서버를 나눠서 API proxy 라우팅 방식을 적용

-> 해결을 위해 다음과 같이 구조를 분기

```
[Control Panel] ──────────▶ [STT Proxy API] ◀───────────────┐
                                  │                         │
                                  ▼                         ▼
                         [stt_cpu Container]       [stt_gpu Container]
                            (Whisper CPU)             (Whisper GPU)
```