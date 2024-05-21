import tkinter as tk
from tkinter import messagebox
import subprocess

def run_upload_script():
    try:
        subprocess.run(['python', 'InputNutrition.py'], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred while running InputNutrition.py: {e}")

def run_ai():
    try:
        subprocess.run(['python', 'AI.py'], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred while running AI.py: {e}")

root = tk.Tk()
root.title("Nutritional Pal")
root.geometry("300x300") 

initial_frame = tk.Frame(root)
initial_frame.pack()

btn_type_input = tk.Button(initial_frame, text="Ask A Question", command=run_ai)
btn_type_input.pack(pady=10)

btn_upload_menu = tk.Button(initial_frame, text="Input Menu", command=run_upload_script)
btn_upload_menu.pack(pady=10)

root.mainloop()
