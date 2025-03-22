from openai import OpenAI
import subprocess
import os
from datetime import datetime
import re
import requests
import tempfile
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import TclError
from tkinter.ttk import Style

# 🔐 API key
client = OpenAI(api_key="YOUR API KEY")

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
    subprocess.run(["osascript", "-e", script])

# === FUNZIONI RTF ===
def linkify(text):
    """Format links as RTF hyperlinks."""
    return re.sub(
        r'(https?://\S+)',
        lambda match: r'\ul\cf1 ' + match.group(1) + r'\cf0\ulnone',
        text
    )

def genera_risposta(prompt):
    """Genera una risposta da ChatGPT basata sul prompt fornito."""
    response = client.chat.completions.create(
        model="gpt-4o-mini-search-preview",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def genera_file(prompt):
    """Genera un file RTF con il contenuto fornito."""
    chiudi_textedit()
    contenuto_testo = genera_risposta(prompt)

    testo_rtf = contenuto_testo  # Scrittura diretta e sicura in RTF
    testo_rtf_linked = linkify(testo_rtf)
    contenuto_testo = contenuto_testo.replace("{", "\\{").replace("}", "\\}").replace("\\", "\\\\")

    # 📁 Trova il file RTF sul desktop
    desktop_path = os.path.expanduser("~/Desktop")
    nome_file = "chat_session.rtf"
    percorso_file = os.path.join(desktop_path, nome_file)

    if os.path.exists(percorso_file):
        with open(percorso_file, "r", encoding="windows-1252") as f:
            contenuto_finale = f.read()
        if not contenuto_finale.endswith("}"):
            contenuto_finale += "}"
        contenuto_finale = contenuto_finale.rstrip("}\n")
    else:
        contenuto_finale = (
            r"{\rtf1\ansi\deff0"
            r"{\fonttbl\f0\fswiss Helvetica;}"
            r"\fs28"  # font size 14pt
            r"\pard\n"
        )

    contenuto_finale += (
        r"\par\pard\sa200\sl276\slmult1" +
        testo_rtf_linked + r"\par\n" +
        "\n".join([scarica_e_converti_img(url) for url in re.findall(r'(https?://\S+\.(?:jpg|jpeg|png|gif|webp))', contenuto_testo, re.IGNORECASE)]) +
        r"\par\n\line\line"
        "}"
    )
    
    # 💾 Salva file su Desktop
    with open(percorso_file, "w", encoding="windows-1252") as file:
        file.write(contenuto_finale)

    import time
    time.sleep(0.5)
    ricarica_textedit(percorso_file)

# 🔽 Scarica e converte immagini in RTF
def scarica_e_converti_img(url):
    """Scarica un'immagine e la converte in formato RTF."""
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        ext = url.split('.')[-1].lower()
        rtf_type = {"jpg": "jpegblip", "jpeg": "jpegblip", "png": "pngblip", "gif": "pngblip", "webp": "pngblip"}.get(ext, "jpegblip")
        hexdata = resp.content.hex()
        rtf_data = (
            r"{\pard\qc{\pict\\" + rtf_type + "\n"
            + "\n".join([hexdata[i:i+128] for i in range(0, len(hexdata), 128)])
            + "\n}}\n"
        )
        return rtf_data
    except Exception as e:
        print(f"Errore con immagine {url}: {e}")
        return r"{\i link immagine non funzionante}"

# === INTERFACCIA GRAFICA (GUI) ===
root = tk.Tk()
root.title("ChatGPT → RTF con immagini")

# Usa il tema di sistema per adattarsi automaticamente a dark/light mode
style = Style()
try:
    style.theme_use(style.theme_use())
except TclError:
    pass

tk.Label(root, text="Scrivi il prompt:").pack(padx=10, pady=5)

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
        messagebox.showwarning("Attenzione", "Inserisci un prompt!")

tk.Button(root, text="Genera file RTF", command=on_generate).pack(pady=10)
entry.bind("<Return>", lambda event: on_generate())

root.mainloop()
