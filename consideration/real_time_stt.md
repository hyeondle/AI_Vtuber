# 🎙️ Whisper 기반 실시간 STT 구현기: Latency와 Streaming 전략에 대한 고민과 해결

## 📌 개요

이 문서는 OpenAI의 Whisper 모델을 이용한 실시간 음성 인식(STT, Speech-to-Text) 시스템을 구현하는 과정에서 발생한 문제, 이론적 분석, 그리고 해결 전략을 담고 있습니다.

특히, 실시간성(latency) 확보를 위한 **pseudo-streaming**, **청크 분리**, **prefix 활용** 등의 기법과, 실제 적용 시 마주친 문제와 그 해결 방안을 구조화하여 정리합니다.

---

## 🎯 1. 목표

- Whisper 모델을 이용한 **실시간 음성 인식** 시스템 구현
- 사용자 발화를 빠르게 텍스트로 변환하여 **LLM → TTS로의 자연스러운 연결**을 만들기 위한 STT 프론트엔드 구현
- 가능한 GPU/CPU 선택 토글이 가능한 구조 유지 (proxy 방식 기반)

---

## 🤔 2. 주요 고민 및 문제 정의

### ❗ 2.1. Latency 문제

- Whisper는 기본적으로 **Batch 처리 기반 모델**로, 긴 오디오를 한 번에 받아 처리함
- 실시간으로 사용하기에는 처리 시간이 너무 길어짐
- 사용자 경험상, 대화가 끝나고 나서 STT가 반응하면 **상호작용이 부자연스러움**

### ❗ 2.2. 문장 경계 처리 & 중복 문제

- 실시간 시스템에서는 발화 중간에 자주 청크가 잘리기 때문에, **문장이 끊기거나 중복되는 현상**이 발생
- Whisper는 반복된 문장 또는 fragment에 대해 동일한 출력을 하므로, 이를 처리할 로직이 필요

---

## 🧠 3. 이론적 배경

### 🧬 3.1. Whisper의 구조

- Transformer 기반 **Encoder-Decoder 모델**
- 입력은 **Mel Spectrogram**
- 디코딩 시 **initial_prompt** (**텍스트 프리픽스**)를 통해 문맥 기반 추론 가능

### 📊 3.2. STT 모델의 일반 처리 방식

- 음향 모델: 오디오 → 특징 추출 (멜 스펙트럼)
- 언어 모델: 특징 → 자연어 텍스트
- Whisper는 이를 end-to-end로 통합한 모델

---

## 🔧 4. 해결 전략: Pseudo-Streaming 구현

### 🧩 4.1. Chunk 기반 오디오 분할

- 오디오를 **2~3초 단위**로 잘라서 Whisper에 전달
- 매 청크마다 **이전 텍스트 결과를 prefix로 주입(initial_prompt)**

```
python
segments, _ = model.transcribe(audio_chunk, initial_prompt=previous_text)
previous_text = "".join([seg.text for seg in segments])
```

---

### 🔁 4.2. Sliding Window + Overlap 전략

- 각 청크를 일정 부분 **겹치게(예: 1초)** 구성하여 문장 경계를 안전하게 처리

```
Chunk 1: [0, 1, 2]
Chunk 2:       [2, 3, 4]
Chunk 3:             [4, 5, 6]
```

- Whisper는 겹치는 오디오를 통해 문맥을 자연스럽게 이어가며 인식

---

### ✂ 4.3. Prefix 기반 중복 제거

- 각 청크에서 생성된 텍스트는 이전 텍스트와 비교하여 중복 제거

```python
def remove_overlap(prefix, new):
    for i in range(len(prefix)):
        if new.startswith(prefix[i:]):
            return new[len(prefix[i:]):]
    return new
```

---

### ⚠️ 4.4. 반복 발화의 중복 제거 문제

- 예: `"no no no"` 와 같은 실제 의미 있는 반복이 제거되는 문제 발생 가능

- 이를 방지하기 위한 예외 처리 로직:

```python
def is_meaningful_repetition(text):
    for word in ["no", "stop", "ha", "yeah"]:
        if f"{word} {word}" in text.lower():
            return True
    return False
```

---

## ⚙️ 5. 성능 영향 요소

| 항목 | 설명 | 개선 방법 |
|------|------|-----------|
| 청크 길이 | 짧으면 빠르지만 정확도↓ | 1.5~2초 추천 |
| 모델 사이즈 | `base`, `small` 적합 | `large`는 실시간 부적합 |
| prefix 길이 | 길수록 느려짐 | 최근 30단어만 유지 |
| 중복 제거 로직 | 문자열 비교 반복 | 보수적 전략 + 캐시 |
| 오디오 버퍼링 | 입출력 지연 발생 가능 | 작은 버퍼 + 비동기 처리 |

---

## ✅ 6. 기대 효과

- Whisper를 **실시간**에 가깝게 사용할 수 있음
- Chunk 간 문맥 연결을 통한 **자연스러운 문장 인식**
- Prefix 및 오버랩 기반으로 **중복 제거 + 문장 경계 안정성 확보**
- LLM, TTS와 연결되는 전체 음성 대화 시스템에서 **실시간성 확보**

---

## 🧪 7. 향후 발전 방향

- [ ] VAD(Voice Activity Detection) 연동으로 무음 시 처리 스킵
- [ ] 동적 chunk size 조절 (예: 사용자의 발화 길이에 따라)
- [ ] 서버-클라이언트 구조로 chunk 전송 최적화
- [ ] GPU 사용 시 auto fallback을 위한 proxy 전환 로직 강화

---

## 📚 참고 자료

- [Whisper GitHub](https://github.com/openai/whisper)
- [Whisper-Streaming: LocalAgreement 알고리즘 기반 실시간 STT](https://github.com/ufal/whisper_streaming)
- [IJCNLP 2023 Demo Paper](https://aclanthology.org/2023.ijcnlp-demo.3.pdf)

---

> STT 기술 사용 중, whisper의 구조와 텍스트 변환에 있어 공부하고 생긴 의문점과 과제 해결을 위해 고민한 내용을 위주로 작성했습니다.
> [실시간 번역 논문](https://aclanthology.org/2023.ijcnlp-demo.3.pdf)을 보고 해당 기술은 사용하기엔 너무 무겁다고 판단, 최대한 가볍고 빠르게 변환할 수 없을까 고민하던 중 나온 결과에 대해 정리해보고 구현해 보았습니다.
