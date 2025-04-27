using UnityEngine;

public class MouthAnimator : MonoBehaviour
{
    private Animator animator;

    private void Start()
    {
        animator = GetComponent<Animator>();
    }

    public void StartSpeaking()
    {
        animator.SetTrigger("Speak");
    }
}
