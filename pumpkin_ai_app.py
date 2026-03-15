# -*- coding: utf-8 -*-
# 南瓜AI智能伴侣 - 基于 DeepSeek API 与 Streamlit
# 运行: ./deepseek_test/run.sh  或  PYTHONUTF8=1 streamlit run pumpkin_ai_app.py
# 利用 001_deepseek_api_test.py 的 API 调用方式

import os
import locale
from pathlib import Path

# 若环境变量未设置，尝试从 .env 加载
if not os.environ.get("DEEPSEEK_API_KEY"):
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).resolve().parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass

# 修复 UnicodeEncodeError: 设置 UTF-8 环境
os.environ.setdefault("LANG", "en_US.UTF-8")
os.environ.setdefault("LC_ALL", "en_US.UTF-8")
if hasattr(locale, "setlocale"):
    try:
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    except Exception:
        try:
            locale.setlocale(locale.LC_ALL, "zh_CN.UTF-8")
        except Exception:
            pass

import json
import streamlit as st

# 会话存储 JSON 路径
SESSION_JSON = Path(__file__).resolve().parent / "sessions.json"

# 页面配置
st.set_page_config(
    page_title="南瓜AI智能伴侣",
    page_icon="🎃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 自定义样式：大标题、布局、侧边栏、固定底部输入框、hover 侧边栏
st.markdown(
    """
<style>
    /* 主内容区底部留空，避免被固定输入框遮挡 */
    .main .block-container {
        padding-bottom: 100px !important;
    }
    /* 固定底部输入框：target 包含 form 的 block */
    [data-testid="stVerticalBlock"] > div:has(form) {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: var(--background-color, #ffffff);
        padding: 1rem 2rem 1.5rem !important;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 999 !important;
    }
    .chat-message {
        padding: 1rem 1.25rem;
        border-radius: 0.5rem;
        margin-bottom: 0.75rem;
        line-height: 1.6;
    }
    .user-msg { background-color: #1e3a5f; color: #f0f4f8; }
    .ai-msg { background-color: #1a3d2e; color: #e8f5e9; }
    [data-testid="stSidebar"] {
        min-width: 280px;
        transition: min-width 0.2s ease, transform 0.2s ease;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        min-width: 2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)
# 侧边栏 hover：左侧移入展开，离开收缩（通过 iframe 注入父页面 script）
st.components.v1.html(
    """
    <script>
    try {
        var p = window.parent;
        if (!p.sidebarHoverDone && p.document) {
            p.sidebarHoverDone = true;
            var s = p.document.createElement('script');
            s.textContent = "(function(){function r(){var e=document.querySelector('[data-testid=stSidebar]');if(!e){setTimeout(r,400);return}var t=document.getElementById('sb-hz');if(!t){t=document.createElement('div');t.id='sb-hz';t.style='position:fixed;left:0;top:0;bottom:0;width:28px;z-index:998;cursor:pointer';document.body.appendChild(t)}t.onmouseenter=function(){if(e.getAttribute('aria-expanded')==='false'){var b=e.querySelector('button');if(b)b.click()}};e.addEventListener('mouseleave',function(){if(e.getAttribute('aria-expanded')==='true'){var b=e.querySelector('button');if(b)b.click()}})}(document.readyState==='loading'?document.addEventListener('DOMContentLoaded',r):r())})();";
            p.document.body.appendChild(s);
        }
    } catch(e) {}
    </script>
    """,
    height=0,
)


def load_sessions() -> dict:
    """从 JSON 加载会话数据"""
    if SESSION_JSON.exists():
        try:
            with open(SESSION_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception:
            pass
    return {
        "history": {"会话_1": []},
        "current_session": "会话_1",
        "session_counter": 1,
        "name": "小南瓜",
        "role": "朋友",
        "personality": "温柔、贴心、幽默",
    }


def save_sessions():
    """将会话数据保存到 JSON"""
    data = {
        "history": st.session_state.history,
        "current_session": st.session_state.current_session,
        "session_counter": st.session_state.session_counter,
        "name": st.session_state.name,
        "role": st.session_state.role,
        "personality": st.session_state.personality,
    }
    try:
        SESSION_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSION_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def init_session_state():
    """初始化 session state，优先从 JSON 加载"""
    if "messages" not in st.session_state:
        data = load_sessions()
        st.session_state.history = data.get("history", {"会话_1": []})
        st.session_state.current_session = data.get("current_session", "会话_1")
        st.session_state.session_counter = data.get("session_counter", 1)
        st.session_state.name = data.get("name", "小南瓜")
        st.session_state.role = data.get("role", "朋友")
        st.session_state.personality = data.get("personality", "温柔、贴心、幽默")
        st.session_state.messages = st.session_state.history.get(
            st.session_state.current_session, []
        ).copy()
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    if "loading" not in st.session_state:
        st.session_state.loading = False


def get_api_key():
    """获取 API Key，未设置时提示并停止"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请设置环境变量 DEEPSEEK_API_KEY")
        st.stop()
    return api_key


def build_system_prompt():
    """根据角色和性格构建系统提示"""
    role_prompts = {
        "恋人": "你是用户的恋人，语气亲密、体贴、充满爱意。",
        "朋友": "你是用户的好朋友，语气轻松、真诚、可以开玩笑。",
        "父母": "你是用户的父母，语气关心、温暖、带有长辈的关怀。",
    }
    role_desc = role_prompts.get(st.session_state.role, role_prompts["朋友"])
    return f"""你是南瓜AI智能伴侣，名字叫{st.session_state.name}。
{role_desc}
你的性格特点：{st.session_state.personality}
请模拟真人与用户实时对话，保持自然、有记忆地延续对话。"""


def call_ai(messages: list) -> str:
    """调用 DeepSeek API（参考 001_deepseek_api_test.py）"""
    get_api_key()  # 确保 API Key 已设置
    from api_client import chat

    system_content = build_system_prompt()
    return chat(messages, system_content=system_content)


def new_conversation():
    """新建会话"""
    save_sessions()  # 先保存当前
    sid = f"会话_{st.session_state.session_counter + 1}"
    st.session_state.session_counter += 1
    st.session_state.current_session = sid
    st.session_state.messages = []
    st.session_state.history[sid] = []
    save_sessions()


def load_history_session(session_id: str):
    """加载历史会话"""
    save_sessions()  # 先保存当前
    st.session_state.current_session = session_id
    st.session_state.messages = st.session_state.history.get(session_id, []).copy()
    save_sessions()


def delete_history_session(session_id: str):
    """删除历史会话"""
    if session_id in st.session_state.history:
        del st.session_state.history[session_id]
    if st.session_state.current_session == session_id:
        first_key = next((k for k in st.session_state.history.keys()), "会话_1")
        st.session_state.current_session = first_key
        st.session_state.messages = st.session_state.history.get(first_key, []).copy()
    save_sessions()


def withdraw_last():
    """撤回最后一条用户消息及其AI回复"""
    if len(st.session_state.messages) >= 2:
        if st.session_state.messages[-1]["role"] == "assistant":
            st.session_state.messages = st.session_state.messages[:-2]
    elif (
        len(st.session_state.messages) == 1
        and st.session_state.messages[-1]["role"] == "user"
    ):
        st.session_state.messages = st.session_state.messages[:-1]


def main():
    init_session_state()

    # 2.1 顶部标题 + 2.5 右上角设置
    col_title, col_settings = st.columns([5, 1])
    with col_title:
        st.components.v1.html(
            '<div style="font-size: 2.5rem; font-weight: bold; text-align: center; color: #FF6B35; margin: 0.5rem 0;">🎃 南瓜ai智能伴侣</div>',
            height=60,
        )
    with col_settings:
        settings_expander = st.popover("⚙️ 设置")
        with settings_expander:
            st.write("**账户功能**")
            if st.button("账户设置"):
                st.info("（演示模式，数据不存储）")
            if st.button("退出账户"):
                st.info("（演示模式）")
            if st.button("切换账户"):
                st.info("（演示模式）")

    # 侧边栏
    with st.sidebar:
        st.subheader("📜 历史会话")
        # 历史会话列表（最近5个）
        history_keys = [k for k in st.session_state.history.keys() if k != "default"]
        display_history = history_keys[-5:][::-1]  # 最近5个，新的在前

        for sid in display_history:
            col_h, col_d = st.columns([3, 1])
            with col_h:
                if st.button(f"📌 {sid}", key=f"load_{sid}", use_container_width=True):
                    load_history_session(sid)
                    st.rerun()
            with col_d:
                if st.button("🗑", key=f"del_{sid}", help="删除"):
                    delete_history_session(sid)
                    st.rerun()

        st.divider()
        if st.button("➕ 新建会话", use_container_width=True):
            new_conversation()
            st.rerun()

        st.divider()
        st.subheader("角色设定")
        st.session_state.name = st.text_input(
            "名字", value=st.session_state.name, key="sidebar_name"
        )
        st.session_state.role = st.selectbox(
            "角色",
            options=["恋人", "朋友", "父母"],
            index=["恋人", "朋友", "父母"].index(st.session_state.role),
            key="sidebar_role",
        )
        st.session_state.personality = st.text_area(
            "性格特点",
            value=st.session_state.personality,
            key="sidebar_personality",
        )

    # 对话区域
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            css = "user-msg" if role == "user" else "ai-msg"
            label = "👤 你" if role == "user" else f"🎃 {st.session_state.name}"
            st.markdown(
                f'<div class="chat-message {css}"><b>{label}</b><br>{content}</div>',
                unsafe_allow_html=True,
            )
        # 思考中时，spinner 显示在对话区域末尾，并在此处调用 AI
        if st.session_state.loading:
            with st.spinner("思考中..."):
                try:
                    ai_reply = call_ai(st.session_state.messages)
                except Exception as e:
                    err_msg = str(e)
                    if "Authentication" in err_msg or "401" in err_msg:
                        ai_reply = "❌ 认证失败：请检查 DEEPSEEK_API_KEY 是否正确、是否已过期，或前往 DeepSeek 控制台确认账户状态。"
                    else:
                        ai_reply = f"❌ 请求失败：{err_msg}"
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.session_state.loading = False
                sid = st.session_state.current_session
                if sid not in st.session_state.history:
                    st.session_state.history[sid] = []
                st.session_state.history[sid] = st.session_state.messages.copy()
                st.session_state.input_key = st.session_state.get("input_key", 0) + 1
                save_sessions()
                st.rerun()

    # 底部输入区（form 支持 Enter 发送，发送按钮需放第一位）
    st.divider()
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_send, col_withdraw = st.columns([6, 1, 1])
        with col_input:
            user_input = st.text_input(
                "输入你的问题",
                placeholder="在这里输入...（按 Enter 发送）",
                key=f"user_input_{st.session_state.get('input_key', 0)}",
                label_visibility="collapsed",
            )
        with col_send:
            send_clicked = st.form_submit_button("发送")
        with col_withdraw:
            withdraw_clicked = st.form_submit_button("撤回")

    if withdraw_clicked:
        withdraw_last()
        sid = st.session_state.current_session
        if sid in st.session_state.history:
            st.session_state.history[sid] = st.session_state.messages.copy()
        save_sessions()
        st.rerun()

    if send_clicked and user_input.strip():
        # 添加用户消息，设置 loading，先 rerun 让 spinner 显示在对话区
        st.session_state.messages.append(
            {"role": "user", "content": user_input.strip()}
        )
        st.session_state.loading = True
        st.rerun()

if __name__ == "__main__":
    main()
