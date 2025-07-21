import streamlit as st 
import ollama

def chat_interface(df):
    if df is None or df.empty:
        st.warning("⚠️ 無法顯示聊天，因為資料尚未載入。")
        return

    summary = df.describe(include='all').to_string()
    st.markdown("請輸入您的分析問題，AI 將根據資料摘要回答：")
    question = st.text_input("🔍 輸入您的問題", placeholder="例如：哪個產品平均種植時間最長？")

    if question:
        with st.spinner("正在分析..."):
            prompt = f"{question}\n\n這是沙拉產品資料摘要：\n{summary}"
            try:
                response = ollama.chat(
                    model="mistral",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown("### 🤖 Ollama 回答：")
                st.write(response['message']['content'])
            except Exception as e:
                st.error(f"❌ 發生錯誤: {str(e)}")
