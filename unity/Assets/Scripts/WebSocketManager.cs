using System;
using System.Text;
using NativeWebSocket;
using UnityEngine;
using System.Threading.Tasks;

public class WebSocketManager : MonoBehaviour
{
    public static WebSocketManager Instance { get; private set; }

    public WebSocket websocket;
    public MouthAnimator mouthAnimator;
    public AudioSource audioSource;

    async void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
            return;
        }

        websocket = new WebSocket("ws://localhost/ws/");
        websocket.OnOpen += () => { Debug.Log("✅ WebSocket 연결 완료"); };
        websocket.OnError += (e) => { Debug.LogError($"❌ WebSocket 에러: {e}"); };
        websocket.OnClose += (e) => { Debug.Log("🔌 WebSocket 연결 종료"); };
        websocket.OnMessage += async (bytes) => { await HandleMessage(bytes); };

        await websocket.Connect();
    }

    void Update()
    {
        if (websocket != null)
        {
            websocket.DispatchMessageQueue();

            // 🔁 재연결 로직
            if (websocket.State == WebSocketState.Closed || websocket.State == WebSocketState.Closing)
            {
                TryReconnect();
            }
        }
    }

    private async void TryReconnect()
    {
        Debug.LogWarning("🔁 WebSocket 재연결 시도 중...");
        await Task.Delay(3000); // 3초 대기
        websocket = new WebSocket("ws://localhost/ws/");
        websocket.OnOpen += () => { Debug.Log("✅ WebSocket 재연결 완료"); };
        websocket.OnError += (e) => { Debug.LogError($"❌ WebSocket 에러: {e}"); };
        websocket.OnClose += (e) => { Debug.Log("🔌 WebSocket 연결 종료"); };
        websocket.OnMessage += async (bytes) => { await HandleMessage(bytes); };
        await websocket.Connect();
    }

    private async Task HandleMessage(byte[] bytes)
    {
        try
        {
            string jsonString = Encoding.UTF8.GetString(bytes);
            MessagePayload payload = JsonUtility.FromJson<MessagePayload>(jsonString);

            if (payload.input_type == "audio")
            {
                Debug.Log("🎵 오디오 수신 및 재생 시작");
                await PlayAudio(payload.audio_b64);
            }
            else if (payload.input_type == "text")
            {
                Debug.Log($"💬 텍스트 수신: {payload.input_text}");
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"[HandleMessage] 오류: {ex}");
        }
    }

    private async Task PlayAudio(string base64Audio)
    {
        try
        {
            byte[] audioBytes = Convert.FromBase64String(base64Audio);

            WAV wav = new WAV(audioBytes);
            AudioClip clip = AudioClip.Create("TTSClip", wav.SampleCount, wav.ChannelCount, wav.Frequency, false);
            clip.SetData(wav.LeftChannel, 0);

            audioSource.clip = clip;
            audioSource.Play();

            // mouthAnimator는 audioSource.isPlaying을 자동 감지해서 애니메이션 상태 변경
        }
        catch (Exception ex)
        {
            Debug.LogError($"[PlayAudio] 오류: {ex}");
        }
        await Task.CompletedTask;
    }

    private void OnApplicationQuit()
    {
        if (websocket != null)
            websocket.Close();
    }
}

[Serializable]
public class MessagePayload
{
    public string input_type;
    public string input_text;
    public string audio_b64;
}
