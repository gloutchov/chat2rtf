from openai import OpenAI
import subprocess
import os
from datetime import datetime
import pypandoc

# 🔐 API key
client = OpenAI(api_key="YOUR API KEY")

# ✍️ Prompt dell'utente
prompt = input("Cosa vuoi che ChatGPT scriva per te? ")

# 📡 Richiesta a ChatGPT
response = client.chat.completions.create(
    model="gpt-4o-mini-search-preview",  # o "gpt-3.5-turbo"
    messages=[{"role": "user", "content": prompt}]
)

# 📄 Contenuto generato
contenuto_testo = response.choices[0].message.content

# 🔄 Conversione da Markdown a RTF
contenuto_rtf = pypandoc.convert_text(contenuto_testo, 'rtf', format='markdown', extra_args=['--standalone'])

# 📁 Salva su Desktop in formato .rtf
nome_file = f"chat_output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.rtf"
percorso_file = os.path.expanduser(f"~/Desktop/{nome_file}")

with open(percorso_file, "w", encoding="utf-8") as file:
    file.write(contenuto_rtf)

# 🚀 Apri con TextEdit
subprocess.run(["open", "-a", "TextEdit", percorso_file])

print(f"✅ File RTF creato e aperto in TextEdit: {percorso_file}")
