# 🥬 C'est la Vie AI 系統

一個用 Python Streamlit 打造的智慧分析工具，支援問答、圖表視覺化與圖片生成。

---

## ✅ 功能介紹

- **💬 問答分析**：用 ChatGPT 模型（Ollama）回答關於產品資料的問題  
- **📊 圖表分析**：顯示平均種植時間、數量統計與狀態比例圖  
- **🎨 圖片生成**：輸入描述，自動產生示意圖  
- **📥 圖表下載**：所有圖表可另存為 PNG

---

## 📦 安裝教學

1. 建立虛擬環境並啟用：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows 用 .\.venv\Scripts\activate

2. 安裝套件: 

pip install -r requirements.txt

3. 安裝並啟動 Ollama 模型：

ollama pull mistral

4. 執行方式

streamlit run app/main.py

打開瀏覽器: http://localhost:8501