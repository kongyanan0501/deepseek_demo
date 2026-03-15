#!/bin/bash
# Railway 等平台通过 PORT 环境变量指定端口
PORT=${PORT:-8080}
exec streamlit run pumpkin_ai_app.py --server.port=$PORT --server.address=0.0.0.0
