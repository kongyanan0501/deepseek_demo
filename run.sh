#!/bin/bash
# 南瓜AI智能伴侣 - 启动脚本（自动加载环境变量 + UTF-8）
cd "$(dirname "$0")/.."
# 加载 shell 配置中的 DEEPSEEK_API_KEY
[ -f ~/.zshrc ] && source ~/.zshrc 2>/dev/null || true
[ -f ~/.bash_profile ] && source ~/.bash_profile 2>/dev/null || true
export PYTHONUTF8=1
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
.venv/bin/streamlit run deepseek_test/pumpkin_ai_app.py "$@"
