#!/bin/bash
# Railway 通过 PORT 环境变量指定端口，用 STREAMLIT_SERVER_PORT 传给 Streamlit
export STREAMLIT_SERVER_PORT=${PORT:-8080}
exec streamlit run pumpkin_ai_app.py --server.address=0.0.0.0
