using System;

public class WAV
{
    public float[] LeftChannel { get; private set; }
    public int ChannelCount { get; private set; }
    public int SampleCount { get; private set; }
    public int Frequency { get; private set; }

    public WAV(byte[] wav)
    {
        if (wav == null || wav.Length < 44)
            throw new ArgumentException("Invalid WAV data.");

        ChannelCount = BitConverter.ToInt16(wav, 22);
        Frequency = BitConverter.ToInt32(wav, 24);

        // **중요**: WAV 파일 헤더(44바이트)를 건너뛴다
        int pos = 44;
        int sampleCount = (wav.Length - pos) / 2;  // 16bit PCM이니까 2바이트 단위
        LeftChannel = new float[sampleCount];
        SampleCount = sampleCount;

        int i = 0;
        while (pos < wav.Length)
        {
            short sample = BitConverter.ToInt16(wav, pos);
            LeftChannel[i++] = sample / 32768.0f;
            pos += 2;
        }
    }
}
