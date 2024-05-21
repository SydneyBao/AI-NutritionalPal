import os
import tkinter as tk
from tkinter import messagebox
from llmware.library import Library
from llmware.retrieval import Query
from llmware.setup import Setup
from llmware.prompts import Prompt
from llmware.configs import LLMWareConfig
from importlib import util
import speech_recognition as sr
import pyttsx3

def clear_placeholder(widget, placeholder, active_color='grey'):
    if widget.get("1.0", tk.END).strip() == placeholder:
        widget.delete('1.0', tk.END)
        widget.config(fg=active_color)

def restore_placeholder(widget, placeholder, inactive_color='grey'):
    if not widget.get("1.0", tk.END).strip():
        widget.insert('1.0', placeholder)
        widget.config(fg=inactive_color)

def semantic_rag(library_name, embedding_model_name, llm_model_name, user_query, output_text, engine):
    library = Library().create_new_library(library_name)
    menu_path = os.path.join("./Documents", "Menu")
    library.add_files(input_folder_path=menu_path, chunk_size=400, max_chunk_size=600, smart_chunking=1)
    library.install_new_embedding(embedding_model_name=embedding_model_name, vector_db="chromadb")

    prompter = Prompt().load_model(llm_model_name)
    results = Query(library).semantic_query(user_query, result_count=50, embedding_distance_threshold=1.0)

    min_distance = float('inf')
    best_entry = None

    for entry in results:
        if entry["distance"] < min_distance:
            min_distance = entry["distance"]
            best_entry = entry

    if best_entry:
        qr = [best_entry]
        prompter.add_source_query_results(query_results=qr)
        response = prompter.prompt_with_source(user_query, prompt_name="default_with_context", temperature=0.3)
        for resp in response:
            if "llm_response" in resp:
                output_text.configure(state='normal')
                clear_placeholder(output_text, "Output will be displayed here...")
                output_text.insert(tk.END, resp["llm_response"] + "\n")
                engine.setProperty('rate', 170)
                engine.setProperty('volume', 0.6)
                voices = engine.getProperty('voices')
                for voice in voices:
                    if "Samantha" in voice.name or "Zira" in voice.name:
                        engine.setProperty('voice', voice.id)
                        break
                    else:
                        engine.setProperty('voice', voices[1].id)
                engine.say(resp["llm_response"])
                engine.runAndWait()
                output_text.configure(state='disabled')
        prompter.clear_source_materials()

    return 0

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("Speech Recognition", "Listening :)")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            query_entry.insert(tk.END, text)
        except sr.UnknownValueError:
            messagebox.showerror("Speech Recognition", "Sorry, I did not understand that.")
        except sr.RequestError as e:
            messagebox.showerror("Speech Recognition", f"Could not request results; {e}")
        except sr.WaitTimeoutError:
            messagebox.showerror("Speech Recognition", "Listening timed out while waiting for phrase to start")

def main():
    LLMWareConfig().set_active_db("sqlite")

    embedding_model = "mini-lm-sbert"
    lib_name = "example_5_library"
    llm_model_name = "llmware/bling-1b-0.1"

    engine = pyttsx3.init()
    root = tk.Tk()
    root.title("Nutritional Pal")
    root.geometry("600x600")

    def run_query(event=None): 
        user_query = query_entry.get("1.0", tk.END).strip()
        if user_query:
            output_text.configure(state='normal')
            clear_placeholder(output_text, "Output will be displayed here...")
            output_text.delete('1.0', tk.END)
            output_text.configure(state='disabled')
            semantic_rag(lib_name, embedding_model, llm_model_name, user_query, output_text, engine)
            query_entry.delete('1.0', tk.END)
            query_entry.config(fg='white')
        return "break"
    
    def add_placeholder(widget, placeholder, inactive_color='grey', active_color='grey'):
        widget.insert('1.0', placeholder)
        widget.config(fg=inactive_color)
        widget.bind("<FocusIn>", lambda event: clear_placeholder(widget, placeholder, active_color))
        widget.bind("<FocusOut>", lambda event: restore_placeholder(widget, placeholder, inactive_color))

    output_text = tk.Text(root, wrap=tk.WORD, width=70, height=15, fg='grey', highlightthickness=0)
    output_text.pack(pady=10)
    add_placeholder(output_text, "hi! I'm here to answer any nutrition questions you may have...")
    output_text.configure(state='disabled')

    global query_entry
    query_entry = tk.Text(root, wrap=tk.WORD, width=70, height=5, fg='white', highlightthickness=0)
    query_entry.pack(pady=10)
    query_entry.focus_set()

    query_entry.bind("<Return>", run_query)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    mic_button = tk.Button(button_frame, text="Speak", command=recognize_speech)
    mic_button.pack(side=tk.LEFT, padx=5)

    query_button = tk.Button(button_frame, text="Submit", command=run_query)
    query_button.pack(side=tk.LEFT, padx=5)

    root.mainloop()

if __name__ == "__main__":
    main()
