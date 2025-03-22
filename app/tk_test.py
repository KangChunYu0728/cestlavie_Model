import tkinter as tk

root = tk.Tk()
root.title("TK Test Window")
root.geometry("300x150")
label = tk.Label(root, text="✅ Tkinter is working!", font=("Arial", 14))
label.pack(pady=30)
root.mainloop()
