
# 🧠 AI VTuber Unity Client (Face-Focused)

이 프로젝트는 AI VTuber를 구현하기 위해 임시로 제작중인 프로젝트입니다.
전체 구조는 `STT → LLM → TTS → Unity`의 실시간 WebSocket 기반 처리 파이프라인을 따릅니다.

---

## 🔁 전체 동작 흐름

```
[1] 사용자 입력 (음성) / 텍스트 입력은 바로 3번으로
   ↓
[2] STT 서비스에서 텍스트로 변환
   ↓
[3] LLM 서비스 (현재 Gemini 2.0)에서 응답 생성 (JSON 포맷 포함)
   ↓
[4] TTS 서비스에서 음성 생성 (WAV Base64)
   ↓
[5] WebSocket 통해 Unity로 전달
   ↓
[6] Unity
   ├─ 음성 재생 (AudioSource)
   ├─ 입모양 반영 (BlendShape)
   └─ 감정값 기반 표정 변화
```

---

## 🔗 WebSocket 통신 메시지 구조

### 📤 클라이언트 → 서버

```json
{
  "type": "text",
  "payload": "춘식아"
}
```

### 📥 서버 → 클라이언트

```json
{
  "input_type": "audio",
  "input_text": "네! 오늘도 좋은 날씨입니다!",
  "audio_b64": "...",
  "unity": {
    "emotion": {
      "happy": 0.8,
      "neutral": 0.2
    },
    "action": "smile"
  }
}
```

---

## 🧩 핵심 스크립트 설명

### `WebSocketManager.cs`

- WebSocket 연결 유지, 메시지 수신
- TTS 음성 데이터를 AudioSource에 재생
- `EmotionDriver` 및 `MouthAnimatorVRM`으로 데이터 전달

### `MouthAnimatorVRM.cs`

- TTS 재생 중일 때만 `BlendShape "{모음}"`를  적용
- 재생이 끝나면 다시 `0.0`으로 전환, Neutral

### `EmotionDriver.cs`

- 서버에서 받은 감정값(`happy`, `angry`, `surprised`, `neutral`)을 `VRMBlendShapeProxy`에 전달
- 모든 값을 수동 초기화 후 재적용

### `AvatarAnchor.cs`

- VRM 모델 위치 및 회전을 씬에서 고정
- 움직임 없는 VTuber 페이스용 설정

---

## 🎛️ 커스터마이징

- BlendShape 감정 키는 VRM에 따라 `"Happy"`, `"Angry"` 등으로 달라질 수 있음 → VRMBlendShapeProxy에서 확인
- 입모양 `"A"` 외에 `"I"`, `"U"` 등 다중 음소 연동도 확장 가능

---

## 📌 설정 가이드

1. Unity 프로젝트에 `UniVRM` 패키지 설치
2. `.vrm` 모델 드래그 후 씬에 배치
3. `Main Camera`에 `FollowHeadCamera.cs` 추가, `faceTarget` 지정
4. VRM 모델 루트에 다음 컴포넌트 연결:
   - `AudioSource`
   - `VRMBlendShapeProxy`
   - `MouthAnimatorVRM`
   - `EmotionDriver`
   - `AvatarAnchor`
5. 실행 시 WebSocket 자동 연결 및 표정 반영 시작

---

## 🧠 예시 결과

- "안녕하세요!" → 입 벌림 `"A"` BlendShape
- 감정 `"happy": 0.9` → 얼굴에 미소 표정 반영
- 음성 출력 없이 표정만도 동작 가능

---

## 🧪 향후 확장

- 눈 깜빡임 (`Blink`) 자동 주기 적용
- 카메라 줌/트래킹 컨트롤 (Zoom, pan)
- 표정 트랜지션 보간 (`Lerp`) 처리
- 행동(action) → 머리끄덕임, 고개 기울임 연동
- 텍스트의 모음을 통해 아, 에, 이, 오, 우를 분석하여 입모양 자동 변화

---

## 🤝 의존성

- Unity 2021 이상
- [UniVRM (https://github.com/vrm-c/UniVRM)](https://github.com/vrm-c/UniVRM)
- WebSocket: `NativeWebSocket`
- VRM 모델: [VRoid Hub 또는 VRM Exporter 활용]

---

## 📍 참고 링크

- [VRM 공식](https://vrm.dev/en/)
- [VRoid Hub](https://hub.vroid.com/)
- [Gemini API](https://ai.google.dev)
- [TTS 모델: GPT-SoVITS / Edge-TTS 등]
