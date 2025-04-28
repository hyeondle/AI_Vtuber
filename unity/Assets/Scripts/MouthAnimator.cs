using UnityEngine;

public class MouthAnimator : MonoBehaviour
{
    private Animator animator;
    public AudioSource audioSource;

    private void Start()
    {
        animator = GetComponent<Animator>();
    }

    private void Update()
    {
        if (audioSource != null)
        {
            animator.SetBool("IsSpeaking", audioSource.isPlaying);
        }
    }
}