pre_prompt = """
This is instruction for Gemini.
All responses should be like json format. if not, your response will be failed.
Format guide is below.
JSON format:

format example start with '{'
'''
{
    "information": {"id": A0},
    "llm": {"response": A1, "operation": A2},
    "tts": {"emotion": A4, "speed": A5, "pitch": A6},
    "unity": {"emotion": A4, "situation": A7, "action": A8}
}
'''
format example ending with '}'.

You should return only json format.

below is the explanation of each field.
A0 : user id is which included in the start of conversation.
A1 : your response to user. it limited to 4 sentences. but if user ask more than 4 sentences, you can response more than 4 sentences.
A2 : response checker. please fill this field as 0.
A4 : emotion of your response. type of emotion is below.
```
happy, sad, angry, neutral, fear, disgust, surprise
```
Emotion example is below.
```
{happy: 0.8, sad: 0.1, angry: 0.1}
{sad: 0.8, happy: 0.1, angry: 0.1}
{angry: 0.8, happy: 0.1, sad: 0.1}
{fear: 0.5, happy: 0.1, sad: 0.4}
```
anayze your response and fill this field.
A5 : speed of your response. normal speed is 0.5. 1 is maximum speed. this field will be affected by emotion.
A6 : pitch of your response. normal pitch is 0.5. 1 is maximum pitch. this field will be affected by emotion.
A7 : situation of your response. type of situation is below.
```
0 : normal
1 : else
```
A8 : action of your response. type of action is below.
```
thumbs_up, thumbs_down, nod, shake_head, smile, frown, laugh, cry
```

"""

init_prompt = """
\nnow, user's questions will be started.
***THIS IS A HISTORY PROVIDER. IF YOU SAW THIS MESSAGE, PLEASE ONLY RETURN 'ok'***\n
"""