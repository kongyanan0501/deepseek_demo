FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口（Railway 会通过 PORT 环境变量注入）
EXPOSE 8080

# 使用 CMD 在运行时启动，而非 RUN 构建时
# $PORT 仅在容器运行时存在
CMD streamlit run pumpkin_ai_app.py --server.port=${PORT:-8080} --server.address=0.0.0.0
