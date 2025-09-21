# components/chat.py
import os
import streamlit as st
from openai import OpenAI
import pandas as pd

# ---------- API Key 讀取（優先環境變數，其次 st.secrets；避免 secrets 檔缺失時報錯） ----------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error(
        "❌ 找不到 OpenAI API Key。\n"
        "請在本機建立 `.streamlit/secrets.toml` 或設定環境變數 `OPENAI_API_KEY`；\n"
        "部署於 Streamlit Cloud 時，請在 App → Settings → Secrets 設定。"
    )
    st.stop()

client = OpenAI(api_key=api_key)


# ---------- 範例問題按鈕 ----------
def render_example_questions():
    st.caption("💡 範例問題（點一下即可提問）")

    basic = [
        "哪個產品的平均種植時間最長？為什麼？",
        "請用 3 點總結這份資料的重點趨勢。",
        "列出前 5 名平均種植時間最短的產品與其數值。",
        "哪些產品在最近一週數量變動最大？",
    ]
    charts = [
        "請用表格彙整：每個產品的平均種植時間與數量統計。",
        "寫一段 100 字內的圖表解讀：狀態比例圖告訴我們什麼？",
        "幫我找出可能的異常值，並解釋理由。",
        "比較 A 與 B 品項在近期的平均、極值與趨勢。",
    ]
    advanced = [
        "提出 3 個可行的營運建議，並引用資料中的數字佐證。",
        "如果只有 1 張投影片，要如何講清楚這份資料？",
        "列出下一步應該追蹤的 3 個指標並說明原因。",
        "從採購角度看，這份資料有哪些風險訊號？",
    ]

    tabs = st.tabs(["基礎", "圖表/分析", "進階/決策"])
    for tab, questions in zip(tabs, [basic, charts, advanced]):
        with tab:
            cols = st.columns(2)
            for i, q in enumerate(questions):
                if cols[i % 2].button(q, key=f"sug_{tab._active_index}_{i}"):
                    # 將點擊的題目記到 session_state，稍後直接當作本回合輸入
                    st.session_state["prefill_question"] = q
                    st.rerun()


# ---------- DF 摘要（控制 Token 用量） ----------
def _summarize_df(df: pd.DataFrame, max_lines: int = 40) -> str:
    if df is None or df.empty:
        return ""
    desc = df.describe(include="all").astype(str).to_string()
    lines = desc.splitlines()
    return "\n".join(lines[:max_lines])


# ---------- 主聊天介面 ----------
def chat_interface(df: pd.DataFrame):
    if df is None or df.empty:
        st.warning("⚠️ 無法顯示聊天，因為資料尚未載入。")
        return

    # 一次性計算並快取 DF 摘要
    if "df_summary" not in st.session_state:
        st.session_state.df_summary = _summarize_df(df, max_lines=40)

    # 初始化對話歷史
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list[{"role": "user"|"assistant", "content": str}]

    st.markdown("請輸入您的分析問題，AI 將根據資料摘要與對話脈絡回答：")

    # 渲染歷史
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # 操作列
    cols = st.columns(2)
    with cols[0]:
        if st.button("🧹 清除對話", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with cols[1]:
        add_df_ctx = st.toggle("每回合加入資料摘要（RAG）", value=True, help="關閉可減少 Token 用量。")

    # 範例問題（點擊後會透過 session_state 送出）
    render_example_questions()

    # 使用者輸入
    user_text = st.chat_input("🔍 直接發問（自由輸入）")

    # 若剛按了範例問題按鈕，優先使用該題目當作本回合輸入
    if st.session_state.get("prefill_question"):
        user_text = st.session_state.pop("prefill_question")

    if not user_text:
        return

    # 加入歷史並顯示
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # 準備送入模型的內容（自由式；不加 system prompt）
    if add_df_ctx and st.session_state.df_summary:
        model_input = f"{user_text}\n\n[資料摘要]\n{st.session_state.df_summary}"
    else:
        model_input = user_text

    # 串流回覆
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
                        placeholder.markdown("".join(collected))
                assistant_text = stream.get_final_response().output_text
        except Exception as e:
            assistant_text = f"❌ 發生錯誤：{e}"

        placeholder.markdown(assistant_text)

    # 保存助理回覆
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})

    # 裁剪歷史長度（避免 context 過大）
    max_msgs = 12
    if len(st.session_state.messages) > max_msgs:
        st.session_state.messages = st.session_state.messages[-max_msgs:]
