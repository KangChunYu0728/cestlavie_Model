import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import json
import ollama
import threading

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
title_label = ttk.Label(root, text=" 數據分析助手", font=("Arial", 18, "bold"))
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

# 讀取 JSON 檔案（手動選擇）
def load_json():
    global json_file_path, json_data
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)  # 讀取 JSON 內容
            json_file_path = file_path  # 儲存 JSON 檔案路徑

            # 更新 UI 顯示已選擇的 JSON 檔案
            json_label.config(text=f"📂 已選擇 JSON：{file_path.split('/')[-1]}")

            messagebox.showinfo("成功", f"✅ JSON 檔案已載入！\n{file_path}")

            # 清除舊的輸出內容，顯示部分 JSON 內容
            output.delete(1.0, tk.END)
            output.insert(tk.END, f"\n📂 已載入 JSON 檔案：{file_path}\n")
            output.insert(tk.END, "\n")
            output.see(tk.END)

        except Exception as e:
            messagebox.showerror("錯誤", f"讀取 JSON 失敗：{e}")
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
    model = "llama2"

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

# 創建按鈕
button_load = ttk.Button(button_frame, text="📂 選擇 JSON 檔案", command=load_json)
button_load.grid(row=0, column=0, padx=10)

button_ask = ttk.Button(button_frame, text="💬 問 Ollama", command=analyze_json)
button_ask.grid(row=0, column=1, padx=10)

# 運行 GUI
root.mainloop()
