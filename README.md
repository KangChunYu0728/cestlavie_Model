# 🥬 C'est la Vie AI

以 **Python + Streamlit** 打造的資料互動式小助手：支援**問答分析**、**圖表視覺化**與**圖片生成**。  
目前已改用 **OpenAI (ChatGPT) API**，可直接部署到 **Streamlit Community Cloud**，無需本機下載/啟動任何模型。

---

## ✨ 功能特色

- **💬 問答分析**：以 ChatGPT 模型回覆（含可選的資料摘要上下文）
- **📊 圖表分析**：平均種植時間、數量統計、狀態比例等
- **🎨 圖片生成**：輸入描述自動產生示意圖
- **📥 圖表下載**：所有圖表可另存為 PNG
- **☁️ 無需本機模型**：改用 OpenAI API，適合部署至 Streamlit Cloud

---

## 🚀 快速開始（本機）

> 建議使用 **Python 3.11**。

1. 安裝套件
````
pip install --upgrade pip
pip install -r requirements.txt

streamlit run main.py

