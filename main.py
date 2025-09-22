import streamlit as st
from components.chat import chat_interface
from components.image_gen import image_generator_ui
from components.chart import chart_analytics_ui
from utils.data_loader import load_data

st.set_page_config(page_title="🥬 C'est la Vie AI", layout="wide")

# Sidebar - Page Selector
st.sidebar.title("🔧 功能選擇")
page = st.sidebar.radio("請選擇功能：", ["💬 問答分析", "📊 圖表分析與圖片生成"])

# Load data
df = load_data()

# 💬 Chat Interface
if page == "💬 問答分析":
    st.title("💬 沙拉米 AI智慧助理")
    chat_interface(df)

# 📊 Analytics + 🎨 Image Generator
elif page == "📊 圖表分析與圖片生成":
    st.title("📊 圖表分析與圖片生成")
    chart_analytics_ui(df)
    st.subheader("🎨 圖片生成")
    image_generator_ui()