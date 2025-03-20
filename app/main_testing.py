import pandas as pd
import subprocess
import ollama
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tkinter as tk
from tkinter import scrolledtext

### ① 檢查是否安裝 Ollama 模型工具
def check_ollama_installed():
    try:
        subprocess.run(["ollama", "--version"], check=True)
        print("✅ 已安裝 Ollama。")
        return True
    except subprocess.CalledProcessError:
        print("❌ 尚未安裝 Ollama，請從 https://ollama.com/download 下載安裝。")
        return False

# ② 下載指定的 Ollama 模型（例如：mistral）
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

# ③ 如果有安裝，則執行模型下載
if check_ollama_installed():
    pull_model("mistral")

### ④ 讀取 Excel 檔案中的產品資料
df = pd.read_excel("/Users/davidkang/Desktop/Cest la Vie/cestlavie_Model/cestlavie_Model/app/merged_product_data_sorted.xlsx")
df["種植日期"] = pd.to_datetime(df["種植日期"])
df["採收日期"] = pd.to_datetime(df["採收日期"])
df["種植時間（日）"] = (df["採收日期"] - df["種植日期"]).dt.days

# ⑤ 將資料摘要（summary）整理成文字格式，提供 AI 分析
summary = df.describe(include='all').to_string()

### ⑥ 建立 GUI 視窗介面
root = tk.Tk()
root.title("🥬 沙拉產品資料 AI 分析系統")
root.geometry("900x600")

# 標籤
label = tk.Label(root, text="請輸入您的分析問題：", font=("Arial", 13))
label.pack(pady=5)

# 問題輸入框
entry = tk.Entry(root, width=100, font=("Arial", 13))
entry.pack(pady=5)

# 回應輸出區（可滾動文字區塊）
output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=20, font=("Arial", 13))
output.pack(pady=10)

### ⑦ 問題送出並回傳 AI 回答
def ask_ollama(event=None):
    question = entry.get()
    if question:
        model = "mistral"
        final_prompt = f"{question}\n\n這是沙拉產品資料摘要：\n{summary}"

        try:
            # 使用 Ollama 模型進行回答
            response = ollama.chat(
                model=model,
                messages=[{'role': 'user', 'content': final_prompt}]
            )
            answer = response['message']['content']
            # 將問題與 AI 回答顯示在 GUI 中
            output.insert(tk.END, f"你: {question}\nOllama 回答:\n{answer}\n\n")
            output.see(tk.END)
            entry.delete(0, tk.END)

            # 顯示圖表分析（可選）
            plot_chart()

        except Exception as e:
            output.insert(tk.END, f"❌ 發生錯誤: {str(e)}\n\n")

### ⑧ 圖表分析功能：顯示各產品的平均種植時間
def plot_chart():
    try:
        plt.figure(figsize=(10, 5))
        sns.barplot(data=df, x="產品名稱", y="種植時間（日）", estimator='mean', errorbar=None)
        plt.title("📈 各產品平均種植時間（日）")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        output.insert(tk.END, f"📉 圖表錯誤: {str(e)}\n\n")

# 綁定 Enter 鍵可直接送出問題
entry.bind("<Return>", ask_ollama)

# 建立送出按鈕
button = tk.Button(root, text="分析資料", command=ask_ollama, font=("Arial", 12))
button.pack(pady=5)

# 啟動 GUI 主迴圈
root.mainloop()
