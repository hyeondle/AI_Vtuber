using System;
using System.Text;
using NativeWebSocket;
using UnityEngine;
using System.Threading.Tasks;
using System.IO;

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

        websocket.OnOpen += () => Debug.Log("✅ WebSocket 연결 완료");
        websocket.OnError += (e) => Debug.LogError($"❌ WebSocket 에러: {e}");
        websocket.OnClose += (e) => Debug.Log("🔌 WebSocket 연결 종료");

        websocket.OnMessage += async (bytes) =>
        {
            Debug.Log($"📥 WebSocket 수신: {bytes.Length} bytes");

            try
            {
                string jsonString = Encoding.UTF8.GetString(bytes);
                MessagePayload payload = JsonUtility.FromJson<MessagePayload>(jsonString);

                if (payload.input_type == "audio")
                {
                    Debug.Log($"🎵 오디오 스트림 수신");

                    if (mouthAnimator != null)
                        mouthAnimator.StartSpeaking();

                    await PlayAudio(payload.audio_b64);
                }
                else if (payload.input_type == "text")
                {
                    Debug.Log($"💬 텍스트 수신: {payload.input_text}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[OnMessage] 오류 발생: {ex}");
            }
        };

        await websocket.Connect();
    }

    void Update()
    {
        if (websocket != null)
        {
            websocket.DispatchMessageQueue();
        }
    }

    private void OnApplicationQuit()
    {
        if (websocket != null)
        {
            websocket.Close();
        }
    }

    private async Task PlayAudio(string base64Audio)
    {
        try
        {
            byte[] audioBytes = Convert.FromBase64String(base64Audio);

            using (MemoryStream stream = new MemoryStream(audioBytes))
            using (BinaryReader reader = new BinaryReader(stream))
            {
                reader.BaseStream.Seek(24, SeekOrigin.Begin);
                int sampleRate = reader.ReadInt32();
                reader.BaseStream.Seek(44, SeekOrigin.Begin);

                byte[] rawData = reader.ReadBytes((int)(stream.Length - 44));
                float[] samples = new float[rawData.Length / 2];
                for (int i = 0; i < samples.Length; i++)
                {
                    short sample = BitConverter.ToInt16(rawData, i * 2);
                    samples[i] = sample / 32768.0f;
                }

                // 채널 수 무조건 1로 강제
                AudioClip clip = AudioClip.Create("TTSClip", samples.Length, 1, sampleRate, false);
                clip.SetData(samples, 0);

                audioSource.clip = clip;
                audioSource.Play();
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"[PlayAudio] 오류: {ex}");
        }

        await Task.CompletedTask;
    }

}

[Serializable]
public class MessagePayload
{
    public string input_type;
    public string input_text;
    public string audio_b64;
}
