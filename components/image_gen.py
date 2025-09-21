import streamlit as st

def image_generator_ui():
    description = st.text_area("🖋️ 輸入圖像描述：", placeholder="例如：一個在田裡種菜的機器人")
    if st.button("生成圖片"):
        if not description:
            st.warning("請先輸入圖像描述。")
            return
        # 🧠 Placeholder: Replace with actual image generation logic using Ollama or API
        st.info(f"👉 模擬圖片生成：'{description}'")
        st.image("https://placekitten.com/400/300", caption="模擬圖像 (測試用)")
