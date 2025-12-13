from openai import OpenAI
from neko_vision import ScreenCapture
client = OpenAI(
    api_key="sk-YodSqbng7IFbfzj0lI4RCb0TgwqVZh3HTGeMCnl4jeg1PVA9",
    base_url="https://yunwu.ai/v1"
)
actions_history = [
    {"role": "system" , "content": "You are a helpful assistant."}
]
def get_actions(prompt):
    global actions_history
    screen = ScreenCapture()
    image64= screen.grab_screen_base64()[0]
    print(image64)
    actions_history.append({
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image64}"
                }
            },
        ]
    })
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=actions_history,
            temperature=0.1,
        )

        assistant_reply = response.choices[0].message.content
        actions_history.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply
    except Exception as e:
        return f"www出错惹: {str(e)}"

print(get_actions(""))
