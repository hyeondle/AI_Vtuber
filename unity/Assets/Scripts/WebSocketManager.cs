using System;
using System.Text;
using NativeWebSocket;
using UnityEngine;
using System.Threading.Tasks;
using UnityEngine.SceneManagement;

public class WebSocketManager : MonoBehaviour
{
    public static WebSocketManager Instance { get; private set; }

    public WebSocket websocket;
    public MouthAnimatorVRM mouthAnimator;
    public AudioSource audioSource;
    public Animator avatarAnimator;
    private bool isReconnecting = false;

    async void Start()
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

        string userId = UserSession.CurrentUserId;
        if (string.IsNullOrEmpty(userId))
        {
            Debug.LogWarning("❌ 유저 ID 없음. InitScene으로 복귀");
            SceneManager.LoadScene("InitScene");
            return;
        }

        websocket = new WebSocket("ws://localhost/ws/");
        websocket.OnOpen += () => {
            Debug.Log("✅ WebSocket 연결 완료");
            // 유저 ID 전송
            var payload = JsonUtility.ToJson(new InitPayload { user_id = userId });
            websocket.SendText(payload);
        };
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

            if (!isReconnecting &&
                (websocket.State == WebSocketState.Closed || websocket.State == WebSocketState.Closing))
            {
                isReconnecting = true;
                TryReconnect();
            }
        }
    }

    private async void TryReconnect()
    {
        Debug.LogWarning("🔁 WebSocket 재연결 시도 중...");
        await Task.Delay(3000); // 3초 대기

        websocket = new WebSocket("ws://localhost/ws/");
        websocket.OnOpen += () => {
            Debug.Log("✅ WebSocket 재연결 완료");

            var payload = JsonUtility.ToJson(new InitPayload { user_id = UserSession.CurrentUserId });
            websocket.SendText(payload);

            isReconnecting = false; // 재연결 성공 후 플래그 해제
        };
        websocket.OnError += (e) => {
            Debug.LogError($"❌ WebSocket 에러: {e}");
            isReconnecting = false; // 실패 시에도 다시 재시도 허용
        };
        websocket.OnClose += (e) => {
            Debug.Log("🔌 WebSocket 연결 종료");
        };
        websocket.OnMessage += async (bytes) => { await HandleMessage(bytes); };

        try
        {
            await websocket.Connect();
        }
        catch (Exception ex)
        {
            Debug.LogError($"[TryReconnect] 예외 발생: {ex.Message}");
            isReconnecting = false; // 연결 실패시 플래그 초기화
        }
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
            else if (payload.input_type == "init")
            {
                Debug.Log("✅ 초기화 성공. Idle 상태로 전환합니다.");
                if (avatarAnimator != null)
                {
                    avatarAnimator.Play("Idle");
                }
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

    public void SendUserId(string userId)
    {
        var payload = new InitPayload { user_id = userId };
        string json = JsonUtility.ToJson(payload);
        websocket.SendText(json);
    }

}

[Serializable]
public class MessagePayload
{
    public string input_type;
    public string input_text;
    public string audio_b64;
}

[Serializable]
public class InitPayload
{
    public string user_id;
}

