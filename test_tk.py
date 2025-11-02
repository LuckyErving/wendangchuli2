#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 Tkinter 是否能正常显示"""

import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
from tkinter import ttk
import sys

print(f"Python 版本: {sys.version}")
print(f"Tkinter 版本: {tk.TkVersion}")

# 创建简单的测试窗口
root = tk.Tk()
root.title("Tkinter 测试")
root.geometry("400x300")

# 添加一些组件
frame = ttk.Frame(root, padding="20")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

label = ttk.Label(frame, text="如果你能看到这个窗口，说明 Tkinter 工作正常！", font=("Arial", 14))
label.grid(row=0, column=0, pady=20)

button = ttk.Button(frame, text="关闭", command=root.quit)
button.grid(row=1, column=0, pady=10)

info_text = f"""
Python: {sys.version.split()[0]}
Tkinter: {tk.TkVersion}
平台: {sys.platform}
"""

info_label = ttk.Label(frame, text=info_text, justify=tk.LEFT)
info_label.grid(row=2, column=0, pady=20)

print("窗口已创建，如果没有显示请检查...")
root.mainloop()
print("测试完成")
