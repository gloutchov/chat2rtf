from openai import OpenAI
import subprocess
import os
from datetime import datetime

# 🔐 La tua API Key
client = OpenAI(api_key="YOUR API KEY")

# 🧠 Prompt dell'utente
prompt = input("Cosa vuoi che ChatGPT scriva per te? ")

# 📡 Chiamata al modello
response = client.chat.completions.create(
    model="gpt-4o-mini-search-preview",
    messages=[{"role": "user", "content": prompt}]
)

# 📝 Contenuto generato
contenuto = response.choices[0].message.content

# 📁 Salvataggio in file .txt
titolo_file = f"chat_output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
percorso = os.path.expanduser(f"~/Desktop/{titolo_file}")

with open(percorso, "w", encoding="utf-8") as file:
    file.write(contenuto)

# 🚀 Apertura con TextEdit
subprocess.run(["open", "-a", "TextEdit", percorso])

print(f"✅ File creato e aperto in TextEdit: {percorso}")
