import tkinter as tk
from tkinter import scrolledtext
import ollama

# 創建 GUI 主視窗
root = tk.Tk()
root.title("Ollama AI Chat")
root.geometry("800x500")

# 創建標籤
label = tk.Label(root, text="請輸入您的問題：", font=("Arial", 12))
label.pack(pady=5)

# 創建輸入框
entry = tk.Entry(root, width=80,font=("Arial", 13))
entry.pack(pady=5)

# 創建回應區
output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=10, font=("Arial", 15))
output.pack(pady=10)

# 初始化 Ollama 客戶端
client = ollama.Client()

# 處理按鈕事件
def ask_ollama(event=None):
    question = entry.get()
    if question:
        model = "llama2"  # 你可以換成其他模型

        # **強制 AI 遵守 20 字限制，並用中文回答**
        system_prompt = "Your response must be under 20 words. Do not exceed this limit under any circumstances."
        system_prompt += " 回答盡量用中文，請一定要遵守這個限制。"

        # **組合最終 Prompt**
        final_prompt = f"{system_prompt}\nQuestion: {question}\nAnswer:"

        try:
            response = client.generate(model=model, prompt=final_prompt)
            output.insert(tk.END, f"你: {question}\nOllama: {response['response']}\n\n")
            output.see(tk.END)
            entry.delete(0, tk.END)  # 清空輸入框
        except Exception as e:
            output.insert(tk.END, f"錯誤: {str(e)}\n\n")

# 綁定 `Enter` 鍵
entry.bind("<Return>", ask_ollama)

# 創建按鈕
button = tk.Button(root, text="詢問 Ollama", command=ask_ollama, font=("Arial", 12))
button.pack(pady=5)

# 運行 GUI
root.mainloop()
