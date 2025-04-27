using System;
using System.Text;
using NativeWebSocket;
using UnityEngine;
using UnityEngine.UI;
using System.Threading.Tasks;

public class ChatInputManager : MonoBehaviour
{
    public InputField chatInputField;
    private WebSocketManager wsManager;

    void Start()
    {
        wsManager = WebSocketManager.Instance;
    }

    void Update()
    {
        if (wsManager != null && wsManager.websocket != null)
        {
            wsManager.websocket.DispatchMessageQueue();
        }

        if (Input.GetKeyDown(KeyCode.Return))
        {
            OnSendChat();
        }
    }

    public async void OnSendChat()
    {
        string message = chatInputField.text.Trim();
        if (!string.IsNullOrEmpty(message) && wsManager != null && wsManager.websocket != null)
        {
            ChatPayload payload = new ChatPayload
            {
                type = "text",
                payload = message
            };
            string json = JsonUtility.ToJson(payload);

            await wsManager.websocket.SendText(json);
            Debug.Log($"📨 보낸 텍스트: {message}");

            chatInputField.text = "";
        }
    }

    private void OnApplicationQuit()
    {
        if (wsManager != null && wsManager.websocket != null)
        {
            wsManager.websocket.Close();
        }
    }
}

[Serializable]
public class ChatPayload
{
    public string type;
    public string payload;
}
