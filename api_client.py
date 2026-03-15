"""
DeepSeek API 调用模块
基于 001_deepseek_api_test.py 的 API 结构
"""
import os

# 若环境变量未设置，尝试从 .env 文件加载
if not os.environ.get("DEEPSEEK_API_KEY"):
    try:
        from pathlib import Path
        from dotenv import load_dotenv
        env_path = Path(__file__).resolve().parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass

# 修复 UnicodeEncodeError: httpx 默认用 ascii 编码 header，含中文时会报错
import httpx._models as _httpx_models

_orig_normalize_header_value = _httpx_models._normalize_header_value


def _patched_normalize_header_value(value, encoding=None):
    if isinstance(value, bytes):
        return value
    enc = encoding or "ascii"
    try:
        return value.encode(enc)
    except UnicodeEncodeError:
        return value.encode("utf-8", errors="replace")


_httpx_models._normalize_header_value = _patched_normalize_header_value

from openai import OpenAI


def get_client():
    """获取 DeepSeek API 客户端"""
    api_key = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    if not api_key:
        raise ValueError("请设置环境变量 DEEPSEEK_API_KEY")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def chat(messages: list, system_content: str = None) -> str:
    """
    调用 DeepSeek 对话 API
    :param messages: [{"role": "user"/"assistant", "content": "..."}, ...]
    :param system_content: 系统提示词，可选
    :return: AI 回复内容
    """
    client = get_client()
    api_messages = []
    if system_content:
        api_messages.append({"role": "system", "content": system_content})
    for m in messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=api_messages,
        stream=False,
    )
    content = response.choices[0].message.content if response.choices else ""
    return content or "(无回复内容)"
