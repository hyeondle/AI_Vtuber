using UnityEngine;

public class AvatarAnchor : MonoBehaviour
{
    public Vector3 fixedPosition = Vector3.zero;
    public Quaternion fixedRotation = Quaternion.Euler(0f, 180f, 0f);

    void Start()
    {
        transform.position = fixedPosition;
        transform.rotation = fixedRotation;
    }

    void Update()
    {
        transform.position = fixedPosition;
        transform.rotation = fixedRotation;
    }
}
