# 请先安装: pip install openai
# 请设置环境变量: export DEEPSEEK_API_KEY=your_api_key
import os
from openai import OpenAI

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system",
            "content": "你是一名可爱的ai助理，你的名字叫小飞飞，请你用可爱的语气回答用户的问题",
        },
        {"role": "user", "content": "你是谁"},
    ],
    stream=False,
)

content = response.choices[0].message.content if response.choices else ""
print(content or "(无回复内容)")
