using UnityEngine;

public class FollowHeadCamera : MonoBehaviour
{
    public Transform faceTarget;
    public Vector3 offset = new Vector3(0f, 0.15f, -0.5f);

    void LateUpdate()
    {
        if (faceTarget == null) return;

        transform.position = faceTarget.position + faceTarget.rotation * offset;
        transform.LookAt(faceTarget.position + Vector3.up * 0.05f);
    }
}
