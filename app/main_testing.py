import pandas as pd
import subprocess
import ollama
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tkinter as tk
from tkinter import scrolledtext
import json
import sys

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

### ④ 讀取 JSON 檔案中的產品資料
def load_data():
    while True:
        try:
            # 取得目前腳本所在的資料夾路徑
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 讓使用者輸入檔案名稱（預設值為 merged_product_data_sorted_json.json）
            default_file = "merged_product_data_sorted_json.json"
            file_name = input(f"請輸入JSON檔案名稱 (直接按 Enter 使用預設檔案 {default_file}，按 'q' 退出): ").strip()
            
            if file_name.lower() == 'q':
                print("程式已退出")
                sys.exit(0)
            
            # 如果使用者沒有輸入，使用預設檔案
            if not file_name:
                file_name = default_file
            
            # 組合完整檔案路徑
            file_path = os.path.join(current_dir, file_name)
            
            # 檢查檔案是否存在
            if not os.path.exists(file_path):
                print(f"❌ 找不到檔案: {file_path}")
                continue
                
            # 檢查檔案副檔名
            if not file_name.endswith('.json'):
                print("❌ 請選擇 JSON 檔案 (.json)")
                continue
            
            print(f"📂 正在讀取檔案: {file_path}")
            
            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.loads(file.read())
            
            # 驗證並過濾資料
            required_columns = ["產品編號", "產品名稱", "種植日期", "採收日期", "狀態"]
            if 'Sheet1' not in json_data:
                raise ValueError("❌ JSON 格式錯誤: 找不到必要的資料欄位 'Sheet1'")
            
            valid_records = []
            invalid_count = 0
            for record in json_data['Sheet1']:
                if all(column in record for column in required_columns):
                    valid_records.append(record)
                else:
                    invalid_count += 1
            
            if not valid_records:
                raise ValueError("沒有找到符合要求的資料記錄")
            
            if invalid_count > 0:
                print(f"已排除 {invalid_count} 筆不完整的資料記錄")
            print(f"❌ 無效的資料記錄數量: {invalid_count}")
            
            # 將 JSON 資料轉換為 DataFrame
            df = pd.DataFrame(valid_records)
            
            # 轉換日期欄位
            df["種植日期"] = pd.to_datetime(df["種植日期"])
            df["採收日期"] = pd.to_datetime(df["採收日期"])
            
            # 計算種植時間
            df["種植時間（日）"] = (df["採收日期"] - df["種植日期"]).dt.days
            
            print("✅ 檔案載入成功！")
            return df
            
        except Exception as e:
            print(f"❌ 讀取資料時發生錯誤: {str(e)}")
        
        retry = input("是否要重試？(y/n): ").lower()
        if retry != 'y':
            print("程式已退出")
            sys.exit(1)

# 載入資料
df = load_data()

# 確保資料成功載入後才繼續執行
if df is not None:
    summary = df.describe(include='all').to_string()
else:
    print("❌ 無法載入資料")
    sys.exit(1)
    
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
        # 設定中文字型
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS','Microsoft YaHei', 'SimHei', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False # 正確顯示負號
        
        while True:
            print("\n可用的圖表選項：")
            print("1. 各產品平均種植時間")
            print("2. 各產品總數量統計")
            print("3. 不同狀態的產品分布")
            print("4. 自定義圖表")
            print("q. 退出")
            
            choice = input("\n請選擇要生成的圖表類型 (1-4 或 q 退出): ").strip()
            
            if choice.lower() == 'q':
                break
                
            plt.figure(figsize=(10, 5))
            
            if choice == '1':
                sns.barplot(data=df, x="產品名稱", y="種植時間（日）", estimator='mean', errorbar=None)
                plt.title("📈 各產品平均種植時間（日）", fontsize=12)
                plt.xlabel("產品名稱", fontsize=10)
                plt.ylabel("種植時間（日）", fontsize=10)
            
            elif choice == '2':
                product_counts = df['產品名稱'].value_counts()
                sns.barplot(x=product_counts.index, y=product_counts.values)
                plt.title("📊 各產品數量統計", fontsize=12)
                plt.xlabel("產品名稱", fontsize=10)
                plt.ylabel("數量", fontsize=10)
            
            elif choice == '3':
                status_counts = df['狀態'].value_counts()
                plt.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
                plt.title("🔄 產品狀態分布", fontsize=12)
            
            elif choice == '4':
                print("\n可用的欄位：")
                numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
                print(", ".join(numeric_columns))
                
                x_col = input("請輸入 X 軸欄位名稱: ").strip()
                y_col = input("請輸入 Y 軸欄位名稱: ").strip()
                
                if x_col in df.columns and y_col in df.columns:
                    sns.barplot(data=df, x=x_col, y=y_col, estimator='mean', errorbar=None)
                    plt.title(f"📊 {x_col} vs {y_col}", fontsize=12)
                    plt.xlabel(x_col, fontsize=10)
                    plt.ylabel(y_col, fontsize=10)
                else:
                    print("❌ 無效的欄位名稱")
                    continue
            
            else:
                print("❌ 無效的選項")
                continue
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
            
            continue_plot = input("\n是否要繼續生成其他圖表？(y/n): ").lower()
            if continue_plot != 'y':
                break
                
    except Exception as e:
        print(f"�� 圖表錯誤: {str(e)}")

# 綁定 Enter 鍵可直接送出問題
entry.bind("<Return>", ask_ollama)

# 建立送出按鈕
button = tk.Button(root, text="分析資料", command=ask_ollama, font=("Arial", 12))
button.pack(pady=5)

# 啟動 GUI 主迴圈
root.mainloop()
