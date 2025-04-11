# 🔁 현재 구조 및 향후 고려

- Whisper는 load_model()로 모델을 미리 불러오는 구조이기 때문에, 컨트롤 패널에서 toggle해도 런타임 중에는 적용이 안 됨
- 이를 해결하려면:
    - 모델을 요청마다 새로 로드하거나
    - GPU 전용 서버와 CPU 서버를 나눠서 API proxy 라우팅 방식을 적용

-> 해결을 위해 다음과 같이 구조를 분기

```
┌──────────────────────────── Client (local execution) ─────────────────────────────┐
│                                                                                   │
│ ┌────────────┐   audio frame   ┌─────────────┐    3sec chunk    ┌───────────────┐ │
│ │  mic input │ ──────────────▶ │ AudioBuffer │ ───────────────▶ │ tiny detector │ │
│ └────────────┘                 └─────────────┘                  └───────┬───────┘ │
│                                                                         │         │
│                                                           speech_detected == true │
│                                                                         ▼         │
│                                                                 ┌───────────────┐ │
│                                                                 │ base STT call │ │
│                                                                 └───────┬───────┘ │
│                                                                         ▼         │
│                                                                   text creation   │
│                                                                         ▼         │
│                                                                  send to LLM, TTS │
└───────────────────────────────────────────────────────────────────────────────────┘

```



# 🎧 시스템 오디오 기반 STT 확장 전략 (Discord / Skype 등)

## ✅ 개요

현재 마이크 입력만을 대상으로 작동하는 실시간 STT 클라이언트 모듈을
**Discord**, **Skype** 등 음성 통화 프로그램과 연계 가능한 시스템 오디오 입력 기반으로 확장하기 위한 방법에 대해 고려한 내용입니다.

---

## 🔁 현재 구조 요약

현재는 `pyaudio`를 사용하여 로컬 **마이크 장치**로부터 입력을 받아,
- `AudioBuffer`에서 3초 청크로 분할하고,
- `tiny` 컨테이너로 발화 여부를 판단한 뒤,
- `stt/cpu` 또는 `stt/gpu` 컨테이너로 텍스트 변환을 수행합니다.

---

## 🎯 목표

- 마이크 대신 **시스템 오디오 출력** (스피커에서 나오는 모든 소리)을 입력으로 설정
- 디스코드, 스카이프 등 음성 채널에 포함된 대화를 자동으로 인식 가능하게 확장
- Whisper 기반 STT 처리 흐름은 동일하게 유지

---

## 🧩 확장 방법

### ✅ 방법 1: 가상 오디오 장치 이용 (macOS/Windows)

#### 사용 도구

| OS        | 추천 도구            |
|-----------|----------------------|
| macOS     | [BlackHole](https://github.com/ExistentialAudio/BlackHole) |
| Windows   | [VB-Audio Cable](https://vb-audio.com/Cable/) |
| Linux     | PulseAudio Monitor (내장) |

#### 설정 절차

1. 가상 장치 설치 및 활성화
2. Discord/Skype 등의 출력 장치를 해당 가상 장치로 설정
3. `pyaudio`에서 해당 장치를 **입력 장치로 선택**

#### 장치 확인 코드

```python
import pyaudio

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(i, info["name"])
```

- 출력 예시:
  ```
  3 BlackHole 2ch
  4 MacBook Pro Microphone
  ```

→ `"BlackHole"` 등의 시스템 오디오 장치를 찾으면 해당 인덱스를 `pyaudio.open()`에 설정

---

### ✅ 방법 2: FFmpeg + PulseAudio (Linux 전용)

```bash
ffmpeg -f pulse -i default -ac 1 -ar 16000 -f wav output.wav
```

- 시스템 오디오를 16kHz, mono로 실시간 녹음
- Whisper 또는 Python 인터페이스로 직접 전달 가능

---

## ⚠️ 주의 사항

| 항목 | 설명 |
|------|------|
| 잡음 포함 가능성 | 시스템 출력 전체를 캡처하기 때문에 알림, 효과음, 음악 등도 포함될 수 있음 |
| 오디오 분리 불가 | Discord 음성만 선택적으로 분리하기 위해선 별도 보이스 API 필요 (복잡도 ↑) |
| 플랫폼 차이 존재 | macOS는 상대적으로 설정 간단, Windows는 드라이버 설치 필요 |

---

## ✅ 기대 효과

- Discord 기반 STT 챗봇 또는 회의 요약 시스템 구현 가능
- 사용자 개입 없이 실시간 음성 모니터링 가능
- Zoom, Skype 등 통합 회의용 AI 확장성 확보

---

## 📌 결론

| 구성 요소 | 확장 가능 여부 | 설명 |
|-----------|----------------|------|
| 시스템 오디오 입력 | ✅ 완전 가능 | 가상 장치 또는 모니터 장치 사용 |
| 구조 변경 필요성 | ❌ 없음 | 입력 장치 변경만으로 기존 코드 사용 가능 |
| Whisper 흐름 영향 | ❌ 없음 | 기존 chunk → detect → base 구조 유지 |

---
