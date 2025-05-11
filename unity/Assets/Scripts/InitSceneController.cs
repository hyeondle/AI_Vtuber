using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class InitSceneController : MonoBehaviour
{
    public InputField userIdInput;
    public GameObject loadingPanel;

    public void OnSubmit()
    {
        string userId = userIdInput.text.Trim();
        if (!string.IsNullOrEmpty(userId))
        {
            loadingPanel.SetActive(true);
            UserSession.CurrentUserId = userId;
            SceneManager.LoadScene("MainScene");
        }
    }
}
