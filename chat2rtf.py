from openai import OpenAI
import os
import subprocess
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pypandoc
   
client = OpenAI(api_key="YOUR API KEY")
contenuto_cache = ""
    
# === FUNZIONI APPLE SCRIPT ===
def chiudi_textedit():
    script = '''
    tell application "TextEdit"
        if it is running then
            try
                close every document saving no
                quit
            end try
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", script])

def ricarica_textedit(percorso_file):
    script = f'''
    tell application "TextEdit"
        set filePath to POSIX file "{percorso_file}" as alias
        try
            repeat with d in documents
                if (path of d as string) is (filePath as string) then
                    close d saving no
                end if
            end repeat
        end try
        open filePath
        activate
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script])
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel riavvio di TextEdit:\n{str(e)}")

# === FUNZIONI RTF ===
def genera_risposta(prompt):
    """Genera una risposta da ChatGPT basata sul prompt fornito."""
    response = client.chat.completions.create(
        model="gpt-4o-mini-search-preview",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def genera_file(prompt):
    global contenuto_cache
    desktop_path = os.path.expanduser("~/Desktop")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # nome_file_rtf = f"chat_session_{timestamp}.rtf"
    nome_file_rtf = f"chat_session.rtf"
    percorso_file_rtf = os.path.join(desktop_path, nome_file_rtf)

    nuova_risposta = genera_risposta(prompt)
    contenuto_cache = contenuto_cache + "\n\n" + nuova_risposta
    
    chiudi_textedit()

    try:
        contenuto_rtf = pypandoc.convert_text(
            contenuto_cache,
            to="rtf",
            format="markdown",
            extra_args=["--standalone"]
        )
    except RuntimeError as e:
        messagebox.showerror("Errore", f"Errore nella conversione in RTF:\n{str(e)}")
        return

    try:
        with open(percorso_file_rtf, "wb") as f:
            f.write(contenuto_rtf.encode("latin1"))
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel salvataggio del file RTF:\n{str(e)}")
        return
    
    time.sleep(0.5)
    ricarica_textedit(percorso_file_rtf)

# === INTERFACCIA GRAFICA (GUI) ===
root = tk.Tk()
root.title("Chat2rtf")

style = ttk.Style()
try:
    style.theme_use(style.theme_use())
except Exception:
    pass

tk.Label(root, text="Domanda:").pack(padx=10, pady=5)

prompt_history = []
entry_var = tk.StringVar()
entry = ttk.Combobox(root, textvariable=entry_var, values=prompt_history, width=60)
entry.pack(padx=10, pady=5)

def on_generate():
    prompt = entry_var.get().strip()
    if prompt:
        if prompt not in prompt_history:
            prompt_history.insert(0, prompt)
            entry["values"] = prompt_history
        genera_file(prompt)
        entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Attenzione", "Inserisci una domanda!")

def azzera_cache():
    global contenuto_cache
    contenuto_cache = ""
    messagebox.showinfo("Cache azzerata", "La cache delle risposte è stata svuotata.")

button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, padx=10, pady=10)

tk.Button(button_frame, text="Azzera Cache", command=azzera_cache).pack(side=tk.LEFT)
tk.Button(button_frame, text="Risposta", command=on_generate).pack(side=tk.RIGHT)

entry.bind("<Return>", lambda event: on_generate())

root.mainloop()
