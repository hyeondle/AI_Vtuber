using UnityEngine;
using VRM;

public class MouthAnimatorVRM : MonoBehaviour
{
    public AudioSource audioSource;
    public float smoothing = 5f;

    private VRMBlendShapeProxy blendShape;
    private float currentValue = 0f;
    private float targetValue = 0f;
    private BlendShapeKey mouthKey;

    void Start()
    {
        blendShape = GetComponent<VRMBlendShapeProxy>();
        mouthKey = BlendShapeKey.CreateUnknown("A");
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space)) {
            blendShape.ImmediatelySetValue(BlendShapeKey.CreateUnknown("A"), 1f);
            Debug.Log("👄 입 벌리기 테스트 실행됨");
        }
        if (audioSource == null || blendShape == null) return;

        targetValue = audioSource.isPlaying ? 1f : 0f;
        currentValue = Mathf.Lerp(currentValue, targetValue, Time.deltaTime * smoothing);

        blendShape.ImmediatelySetValue(mouthKey, currentValue);
    }
}
