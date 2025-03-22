from openai import OpenAI
import subprocess
import os
from datetime import datetime
import pypandoc
import re
import requests
import tempfile

# 🔐 API key
client = OpenAI(api_key="YOUR API KEY")

# ✍️ Prompt dell'utente
prompt = input("Cosa vuoi che ChatGPT scriva per te? ")

# 📡 Richiesta a ChatGPT
response = client.chat.completions.create(
    model="gpt-4o-mini-search-preview",  # o "gpt-3.5-turbo"
    # model="gpt-4o",  # o "gpt-3.5-turbo"
    messages=[{"role": "user", "content": prompt}]
)

# 📄 Contenuto generato
contenuto_testo = response.choices[0].message.content

# 🔍 Estrai URL immagine dal testo
img_urls = re.findall(r'(https?://\S+\.(?:jpg|jpeg|png|gif|webp))', contenuto_testo, re.IGNORECASE)

# 🔽 Scarica e converte immagini in RTF
def scarica_e_converti_img(url):
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

# 🔁 Crea blocchi RTF per tutte le immagini
immagini_rtf = "\n".join([scarica_e_converti_img(url) for url in img_urls])

# 🔠 Converte testo in RTF
testo_rtf = pypandoc.convert_text(contenuto_testo, 'rtf', format='markdown', extra_args=['--standalone'])

# 📎 Unisce testo + immagini
contenuto_finale = (
    r"{\rtf1\ansi\deff0\n" +
    testo_rtf +
    "\n" +
    immagini_rtf +
    "\n}"
)

# 💾 Salva file su Desktop
nome_file = f"chat_output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.rtf"
percorso_file = os.path.expanduser(f"~/Desktop/{nome_file}")

with open(percorso_file, "w", encoding="utf-8") as file:
    file.write(contenuto_finale)

# 🚀 Apri in TextEdit
subprocess.run(["open", "-a", "TextEdit", percorso_file])

print(f"✅ File RTF con immagini creato: {percorso_file}")
