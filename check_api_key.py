#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 DEEPSEEK_API_KEY 是否已正确配置"""
import os
import sys

# 尝试从 .env 加载
try:
    from pathlib import Path
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"已从 {env_path} 加载 .env")
except ImportError:
    pass

key = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()
if not key:
    print("❌ DEEPSEEK_API_KEY 未设置或为空")
    print("\n请选择以下方式之一：")
    print("1. 在终端执行: export DEEPSEEK_API_KEY=你的key")
    print("2. 创建 .env 文件: cp .env.example .env  然后编辑填入 key")
    print("3. 在 ~/.zshrc 添加: export DEEPSEEK_API_KEY=你的key  然后 source ~/.zshrc")
    sys.exit(1)

print(f"✅ DEEPSEEK_API_KEY 已设置")
print(f"   长度: {len(key)}")
print(f"   前缀: {key[:6]}...")
if not key.startswith("sk-"):
    print("⚠️  警告: Key 通常以 sk- 开头，请确认是否正确")
