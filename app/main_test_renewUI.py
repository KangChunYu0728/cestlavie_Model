import pandas as pd
import subprocess
import ollama
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import sys
import threading

### ④ 讀取 JSON 檔案中的產品資料
def load_data(file_path):
    try:
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
        return None

# 初始化 Tkinter GUI
root = tk.Tk()
root.title("數據分析助手")
root.geometry("900x700")
root.configure(bg="#f0f2f5")  # 設定背景色

# 設定 ttk 風格
style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=10)
style.configure("TLabel", font=("Arial", 12), background="#f0f2f5")
style.configure("TEntry", font=("Arial", 12), padding=5)
style.configure("TFrame", background="#f0f2f5")

# 創建標題
title_label = ttk.Label(root, text="數據分析助手", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

# 創建按鈕框架
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

# 顯示當前 JSON 檔案名稱
json_label = ttk.Label(root, text="📂 未選擇 JSON 檔案", font=("Arial", 12))
json_label.pack()

# 創建回應區
output_label = ttk.Label(root, text="💬 Ollama AI 分析結果：")
output_label.pack()
output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=15, font=("Arial", 13))
output.pack(pady=10)

# 創建用戶輸入問題的區域
question_label = ttk.Label(root, text="📌 請輸入您的問題：")
question_label.pack()
question_entry = ttk.Entry(root, width=80, font=("Arial", 13))
question_entry.pack(pady=7)

# 初始化 `Ollama`
client = ollama.Client()

# 全域變數存儲 JSON 檔案位置 & 內容
json_file_path = None
json_data = None
df = None
summary = None

# 讀取 JSON 檔案（手動選擇）
def load_json():
    global json_file_path, json_data, df, summary
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        df = load_data(file_path)
        if df is not None:
            json_file_path = file_path
            summary = df.describe(include='all').to_string()

            # 更新 UI 顯示已選擇的 JSON 檔案
            json_label.config(text=f"📂 已選擇 JSON：{file_path.split('/')[-1]}")

            messagebox.showinfo("成功", f"✅ JSON 檔案已載入！\n{file_path}")

            # 清除舊的輸出內容，顯示部分 JSON 內容
            output.delete(1.0, tk.END)
            output.insert(tk.END, f"\n📂 已載入 JSON 檔案：{file_path}\n")
            output.insert(tk.END, "\n")
            output.see(tk.END)
        else:
            messagebox.showerror("錯誤", "讀取 JSON 失敗")
    else:
        messagebox.showwarning("⚠️ 警告", "未選擇任何 JSON 檔案！")

# 讓 `Ollama` 分析 JSON
def analyze_json():
    if json_file_path is None:
        messagebox.showwarning("⚠️ 警告", "請先載入 JSON 檔案！")
        return

    threading.Thread(target=process_ollama, daemon=True).start()

# 讓 `Ollama` 處理用戶問題
def process_ollama():
    global json_data
    model = "llama3"

    # 設定 Prompt
    question = question_entry.get().strip()
    if not question:
        messagebox.showwarning("⚠️ 警告", "請輸入您的問題！")
        return

    system_prompt = f"""
    你是一名專業的數據分析專家，你的回應**必須嚴格基於以下數據**，**不可編造或推測**，**只能引用提供的資訊**。
    此外，**你的回答必須使用標準中文**，不得使用任何其他語言。

     **規則**
    - **你只能根據的數據回答**，**如果數據中沒有相關資訊，請回答「無相關資訊」**。
    - **你不可以編造或猜測**，只能引用資料。
    - **你的回答必須完全用中文**，不可以包含英文、拼音或其他語言。

     **以下是數據**
    {json.dumps(json_data, ensure_ascii=False, indent=4)}

     **用戶問題**：{question}
    """

    # 發送給 `Ollama`
    try:
        output.insert(tk.END, f"\n 你: {question}\n Ollama: ⏳ 分析中...\n")
        output.see(tk.END)
        output.update_idletasks()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"請按照提供的資訊回答，並且輸出標準的中文回答。\n\n數據：\n{json.dumps(json_data, ensure_ascii=False, indent=4)}"},
            {"role": "user", "content": f"**用戶問題**：{question}"}
        ]

        response = client.chat(model=model, messages=messages, stream=True)

        for chunk in response:
            output.insert(tk.END, chunk["message"]["content"])

        output.insert(tk.END, "\n\n✅ 分析完成。\n")
        question_entry.delete(0, tk.END)  # 清空輸入框

    except Exception as e:
        output.insert(tk.END, f"❌ 錯誤: {str(e)}\n\n")

# 創建圖表按鈕的回調函數
def plot_chart(choice):
    try:
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False  # 正確顯示負號

        plt.figure(figsize=(10, 5))

        if choice == '1':
            sns.barplot(data=df, x="產品名稱", y="種植時間（日）", estimator='mean', errorbar=None)
            plt.title(" 各產品平均種植時間（日）", fontsize=12)
            plt.xlabel("產品名稱", fontsize=10)
            plt.ylabel("種植時間（日）", fontsize=10)

        elif choice == '2':
            product_counts = df['產品名稱'].value_counts()
            sns.barplot(x=product_counts.index, y=product_counts.values)
            plt.title(" 各產品數量統計", fontsize=12)
            plt.xlabel("產品名稱", fontsize=10)
            plt.ylabel("數量", fontsize=10)

        elif choice == '3':
            status_counts = df['狀態'].value_counts()
            plt.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
            plt.title(" 產品狀態分布", fontsize=12)

        elif choice == '4':
            # 使用下拉選單選擇 X 軸和 Y 軸欄位
            def generate_custom_chart():
                x_col = x_combobox.get()
                y_col = y_combobox.get()

                if x_col in df.columns and y_col in df.columns:
                    plt.figure(figsize=(10, 5))
                    sns.barplot(data=df, x=x_col, y=y_col, estimator='mean', errorbar=None)
                    plt.title(f" {x_col} vs {y_col}", fontsize=12)
                    plt.xlabel(x_col, fontsize=10)
                    plt.ylabel(y_col, fontsize=10)
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    plt.show()
                else:
                    messagebox.showerror("錯誤", "請選擇有效的欄位！")

            # 創建新窗口
            custom_chart_window = tk.Toplevel(root)
            custom_chart_window.title("自定義圖表")
            custom_chart_window.geometry("400x200")

            # 下拉選單選擇 X 軸和 Y 軸欄位
            ttk.Label(custom_chart_window, text="選擇 X 軸欄位：").pack(pady=5)
            x_combobox = ttk.Combobox(custom_chart_window, values=list(df.columns), state="readonly")
            x_combobox.pack(pady=5)

            ttk.Label(custom_chart_window, text="選擇 Y 軸欄位：").pack(pady=5)
            y_combobox = ttk.Combobox(custom_chart_window, values=list(df.columns), state="readonly")
            y_combobox.pack(pady=5)

            # 確認按鈕
            confirm_button = ttk.Button(custom_chart_window, text="生成圖表", command=generate_custom_chart)
            confirm_button.pack(pady=10)

        else:
            messagebox.showerror("錯誤", "無效的選項！")
            return

        if choice != '4':  # 自定義圖表不需要立即顯示
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()

    except Exception as e:
        messagebox.showerror("錯誤", f"圖表生成失敗：{str(e)}")

# 創建圖表按鈕
chart_buttons_frame = ttk.Frame(root)
chart_buttons_frame.pack(pady=10)

chart_button_1 = ttk.Button(chart_buttons_frame, text="各產品平均種植時間", command=lambda: plot_chart('1'))
chart_button_1.grid(row=0, column=0, padx=10)

chart_button_2 = ttk.Button(chart_buttons_frame, text="各產品總數量統計", command=lambda: plot_chart('2'))
chart_button_2.grid(row=0, column=1, padx=10)

chart_button_3 = ttk.Button(chart_buttons_frame, text="不同狀態的產品分布", command=lambda: plot_chart('3'))
chart_button_3.grid(row=0, column=2, padx=10)

chart_button_4 = ttk.Button(chart_buttons_frame, text="自定義圖表", command=lambda: plot_chart('4'))
chart_button_4.grid(row=0, column=3, padx=10)


# 定義 ask_ollama 函數
def ask_ollama(event=None):
    question = question_entry.get()
    if question:
        model = "llama3"
        final_prompt = f"{question}\n\n這是沙拉產品資料摘要：\n{summary}，請用中文回答問題。"

        try:
            # 使用 Ollama 模型進行回答
            response = client.chat(
                model=model,
                messages=[{'role': 'user', 'content': final_prompt}],
                stream=True,
            )

            # 初始化變量來存儲完整回答
            full_answer = ""

            # 實時處理生成器的內容
            for chunk in response:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    full_answer += content  # 累積完整回答
                    output.insert(tk.END, content)  # 即時顯示回應內容
                    output.see(tk.END)
                    output.update_idletasks()  # 確保即時更新

            # 將問題與完整回答顯示在 GUI 中
            output.insert(tk.END, f"\n你: {question}\nOllama 回答:\n{full_answer}\n\n")
            output.see(tk.END)
            question_entry.delete(0, tk.END)  # 清空輸入框

        except Exception as e:
            # 捕獲異常並顯示錯誤信息
            output.insert(tk.END, f"❌ 發生錯誤: {str(e)}\n\n")
            messagebox.showerror("錯誤", f"處理問題時發生錯誤：{str(e)}")




# 綁定 Enter 鍵可直接送出問題
question_entry.bind("<Return>", ask_ollama)

# 建立選擇 JSON 檔案的按鈕
button_load = ttk.Button(button_frame, text="📂 選擇 JSON 檔案", command=load_json)
button_load.grid(row=0, column=0, padx=10)

# 建立分析資料的按鈕
button_ask = ttk.Button(button_frame, text="💬 問 Ollama", command=analyze_json)
button_ask.grid(row=0, column=1, padx=10)

# 建立送出按鈕
button = ttk.Button(root, text="分析資料", command=ask_ollama)
button.pack(pady=5)

# 啟動 GUI 主迴圈
root.mainloop()
