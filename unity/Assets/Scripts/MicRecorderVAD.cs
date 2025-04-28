using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using System.Threading.Tasks;

public class MicRecorderVAD : MonoBehaviour
{
    public static MicRecorderVAD Instance { get; private set; }

    public int sampleRate = 16000;
    public float silenceThreshold = 0.01f; // 에너지 기준값
    public float silenceDuration = 1.0f; // 종료판단 시간
    public float checkInterval = 0.1f; // 에너지 체크 주기

    private AudioClip recordingClip;
    private bool isRecording = false;
    private List<float> recordedSamples = new List<float>();

    private float silenceTimer = 0.0f;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    public void StartVADRecording()
    {
        if (Microphone.devices.Length == 0)
        {
            Debug.LogError("🎙️ 마이크 장치 없음");
            return;
        }

        recordingClip = Microphone.Start(null, true, 30, sampleRate);
        isRecording = true;
        recordedSamples.Clear();
        silenceTimer = 0f;

        Debug.Log("🎤 음성 감지 녹음 시작");
        InvokeRepeating(nameof(CheckVoiceActivity), 0f, checkInterval);
    }

    private void CheckVoiceActivity()
    {
        if (!isRecording || recordingClip == null) return;

        int position = Microphone.GetPosition(null);
        float[] samples = new float[1024];
        recordingClip.GetData(samples, position - samples.Length >= 0 ? position - samples.Length : 0);

        float energy = 0f;
        foreach (float sample in samples)
        {
            energy += Mathf.Abs(sample);
        }
        energy /= samples.Length;

        if (energy > silenceThreshold)
        {
            silenceTimer = 0f;
            recordedSamples.AddRange(samples);
        }
        else
        {
            silenceTimer += checkInterval;
            if (silenceTimer >= silenceDuration && recordedSamples.Count > 0)
            {
                Debug.Log("🛑 음성 종료 감지, 녹음 저장 및 전송");
                StopVADRecordingAndSend();
            }
        }
    }


    private async void StopVADRecordingAndSend()
    {
        CancelInvoke(nameof(CheckVoiceActivity));
        isRecording = false;
        Microphone.End(null);

        byte[] wavBytes = ConvertToWav(recordedSamples.ToArray(), 1, sampleRate);
        string base64Audio = Convert.ToBase64String(wavBytes);

        var payload = new MicPayload
        {
            type = "audio",
            payload = base64Audio
        };
        string json = JsonUtility.ToJson(payload);

        if (WebSocketManager.Instance != null && WebSocketManager.Instance.websocket != null)
        {
            await WebSocketManager.Instance.websocket.SendText(json);
            Debug.Log("📤 오디오 데이터 전송 완료");
        }
    }


    private byte[] ConvertToWav(float[] samples, int channels, int sampleRate)
    {
        int byteLength = samples.Length * 2;
        int fileSize = 44 + byteLength;
        byte[] bytes = new byte[fileSize];

        Encoding.ASCII.GetBytes("RIFF").CopyTo(bytes, 0);
        BitConverter.GetBytes(fileSize - 8).CopyTo(bytes, 4);
        Encoding.ASCII.GetBytes("WAVE").CopyTo(bytes, 8);

        Encoding.ASCII.GetBytes("fmt ").CopyTo(bytes, 12);
        BitConverter.GetBytes(16).CopyTo(bytes, 16);
        BitConverter.GetBytes((short)1).CopyTo(bytes, 20);
        BitConverter.GetBytes((short)channels).CopyTo(bytes, 22);
        BitConverter.GetBytes(sampleRate).CopyTo(bytes, 24);
        BitConverter.GetBytes(sampleRate * channels * 2).CopyTo(bytes, 28);
        BitConverter.GetBytes((short)(channels * 2)).CopyTo(bytes, 32);
        BitConverter.GetBytes((short)16).CopyTo(bytes, 34);

        Encoding.ASCII.GetBytes("data").CopyTo(bytes, 36);
        BitConverter.GetBytes(byteLength).CopyTo(bytes, 40);

        int offset = 44;
        foreach (float sample in samples)
        {
            short intSample = (short)(sample * 32767f);
            BitConverter.GetBytes(intSample).CopyTo(bytes, offset);
            offset += 2;
        }

        return bytes;
    }
}

[Serializable]
public class MicPayload
{
    public string type;
    public string payload;
}
