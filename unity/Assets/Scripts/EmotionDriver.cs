using UnityEngine;
using System.Collections.Generic;
using VRM;

public class EmotionDriver : MonoBehaviour
{
    private VRMBlendShapeProxy proxy;

    void Start()
    {
        proxy = GetComponent<VRMBlendShapeProxy>();
    }

    public void ApplyEmotion(Dictionary<string, float> emotions)
    {
        if (proxy == null) return;

        ClearBlendShapes();

        foreach (var pair in emotions)
        {
            var key = BlendShapeKey.CreateUnknown(pair.Key);
            proxy.SetValue(key, pair.Value);
        }

        proxy.Apply();
    }

    private void ClearBlendShapes()
    {
        foreach (var pair in proxy.GetValues())
        {
            proxy.SetValue(pair.Key, 0f);
        }
    }
}
