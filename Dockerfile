FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口（Railway 会通过 PORT 环境变量注入）
EXPOSE 8080

# 使用启动脚本确保 PORT 正确展开
RUN chmod +x start.sh
CMD ["./start.sh"]
