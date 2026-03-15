# DeepSeek API 测试

## 南瓜AI智能伴侣

基于需求文档开发的 AI 对话应用，使用 Streamlit + DeepSeek API。

**运行：**
```bash
cd /Users/huangdeyu/Documents/kyn/code/python
PYTHONUTF8=1 .venv/bin/streamlit run deepseek_test/pumpkin_ai_app.py
```

若遇 `UnicodeEncodeError`，请使用 `PYTHONUTF8=1` 前缀运行。

## 简单 API 测试

```bash
.venv/bin/python deepseek_test/001_deepseek_api_test.py
```

## 环境变量

需设置 `DEEPSEEK_API_KEY`：
```bash
export DEEPSEEK_API_KEY=your_api_key
```
