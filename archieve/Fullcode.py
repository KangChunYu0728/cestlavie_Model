import pandas as pd
import subprocess
import ollama
import matplotlib.pyplot as plt
import seaborn as sns
import os
import streamlit as st
import json

# ① 檢查是否安裝並下載 Ollama 模型
def check_ollama_installed():
    try:
        subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.DEVNULL)
        print("✅ 已安裝 Ollama。")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 尚未安裝 Ollama，請從 https://ollama.com/download 下載安裝。")
        return False

def is_model_pulled(model_name="mistral"):
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        return model_name in result.stdout
    except Exception:
        return False

def pull_model(model_name="mistral"):
    try:
        print(f"📦 正在下載模型 '{model_name}'...")
        process = subprocess.Popen(["ollama", "pull", model_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line.strip())
        process.wait()
        if process.returncode == 0:
            print(f"✅ 模型 '{model_name}' 下載完成！")
        else:
            print("❌ 模型下載失敗。")
    except Exception as e:
        print("錯誤:", e)

if check_ollama_installed() and not is_model_pulled("mistral"):
    pull_model("mistral")


# ② 載入產品資料 JSON
@st.cache_data
def load_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "Data/merged_product_data_sorted_json.json")

        if not os.path.exists(file_path):
            st.error(f"❌ 找不到檔案: {file_path}")
            st.stop()

        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        required_columns = ["產品編號", "產品名稱", "種植日期", "採收日期", "狀態"]
        if 'Sheet1' not in json_data:
            st.error("❌ JSON 格式錯誤：找不到 'Sheet1' 欄位")
            st.stop()

        valid_records = [
            record for record in json_data['Sheet1']
            if all(col in record for col in required_columns)
        ]

        if not valid_records:
            st.error("❌ 沒有符合要求的資料記錄")
            st.stop()

        df = pd.DataFrame(valid_records)
        df["種植日期"] = pd.to_datetime(df["種植日期"])
        df["採收日期"] = pd.to_datetime(df["採收日期"])
        df["種植時間（日）"] = (df["採收日期"] - df["種植日期"]).dt.days

        return df

    except Exception as e:
        st.error(f"❌ 載入資料時發生錯誤: {str(e)}")
        st.stop()


# ③ 建立 Streamlit 應用
st.set_page_config(layout="wide", page_title="🥬 沙拉產品資料 AI 分析系統")
st.title("🥬 沙拉產品資料 AI 分析系統")

# 把資料載入模型
df = load_data()

if df is not None and not df.empty:
    summary = df.describe(include='all').to_string()
else:
    st.error("無法載入有效的資料， 請確認JSON格式或內容!!")
    st.stop

st.markdown("請輸入您的分析問題，AI 將根據資料摘要回答：")
question = st.text_input("🔍 輸入您的問題", placeholder="例如：哪個產品平均種植時間最長？")


# ④ 問題送出並取得 AI 回答
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

# ⑤ 圖表分析區塊
st.divider()
st.subheader("📊 資料圖表分析")

chart_option = st.selectbox("請選擇要產生的圖表：", [
    "各產品平均種植時間",
    "各產品總數量統計",
    "不同狀態的產品分布",
    "自定義圖表"
])

if chart_option == "不同狀態的產品分布":
    try:
        status_counts = df["狀態"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
        ax.set_title("🔄 不同狀態的產品分布")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"❌ 圖表錯誤: {str(e)}")
else:
    fig = plt.figure(figsize=(10, 5))
    try:
        if chart_option == "各產品平均種植時間":
            sns.barplot(data=df, x="產品名稱", y="種植時間（日）", estimator='mean', errorbar=None)
            plt.title("📈 各產品平均種植時間（日）")

        elif chart_option == "各產品總數量統計":
            counts = df["產品名稱"].value_counts()
            sns.barplot(x=counts.index, y=counts.values)
            plt.title("📊 各產品總數量統計")
            plt.xlabel("產品名稱")
            plt.ylabel("數量")

        elif chart_option == "自定義圖表":
            x_col = st.selectbox("選擇 X 軸欄位", options=df.columns, key="xcol")
            y_col = st.selectbox("選擇 Y 軸欄位", options=df.select_dtypes(include=['int64', 'float64']).columns, key="ycol")
            sns.barplot(data=df, x=x_col, y=y_col, estimator='mean', errorbar=None)
            plt.title(f"📊 {x_col} vs {y_col}")

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ 圖表錯誤: {str(e)}")
