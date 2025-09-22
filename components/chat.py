# component/chat.py
import streamlit as st
from openai import OpenAI
import pandas as pd

# Use secrets for key (works locally + Streamlit Cloud)
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ 找不到 OpenAI API Key。請在 .streamlit/secrets.toml 或環境變數中設定 `OPENAI_API_KEY`。")
    st.stop()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def _summarize_df(df: pd.DataFrame, max_lines: int = 40) -> str:
    """Compact DF summary to control token usage."""
    if df is None or df.empty:
        return ""
    desc = df.describe(include="all").astype(str).to_string()
    lines = desc.splitlines()
    return "\n".join(lines[:max_lines])

def chat_interface(df: pd.DataFrame):
    if df is None or df.empty:
        st.warning("⚠️ 無法顯示聊天，因為資料尚未載入。")
        return

    # One-time compute & cache a lightweight DF summary
    if "df_summary" not in st.session_state:
        st.session_state.df_summary = _summarize_df(df, max_lines=40)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list[{"role": "user"|"assistant", "content": str}]

    st.markdown("歡迎問任何跟種植有關問題，AI 將根據資料摘要與對話脈絡回答：")

    # Render history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Controls
    cols = st.columns(2)
    with cols[0]:
        if st.button("🧹 清除對話", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with cols[1]:
        add_df_ctx = st.toggle("每回合加入資料摘要（RAG）", value=True, help="關閉可減少 Token 用量。")

    # User input
    user_text = st.chat_input("🔍 直接發問（自由輸入）")
    if not user_text:
        return

    # Append user message to history
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # Prepare model input (free-form; no system msg)
    if add_df_ctx and st.session_state.df_summary:
        model_input = f"{user_text}\n\n[資料摘要]\n{st.session_state.df_summary}"
    else:
        model_input = user_text

    # Stream the assistant reply
    with st.chat_message("assistant"):
        placeholder = st.empty()
        collected = []

        try:
            with client.responses.stream(
                model="gpt-4o-mini",
                input=model_input,
                temperature=0.2,
            ) as stream:
                for event in stream:
                    if event.type == "response.output_text.delta":
                        collected.append(event.delta)
                        # Efficient incremental render
                        placeholder.markdown("".join(collected))
                # Final text
                assistant_text = stream.get_final_response().output_text
        except Exception as e:
            assistant_text = f"❌ 發生錯誤：{e}"

        placeholder.markdown(assistant_text)

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})

    # Optional: trim history to avoid huge context (keeps last 12 messages = 6 turns)
    max_msgs = 12
    if len(st.session_state.messages) > max_msgs:
        st.session_state.messages = st.session_state.messages[-max_msgs:]
