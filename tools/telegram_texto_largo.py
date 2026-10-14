"""Manda un archivo de texto por Telegram: el contenido en mensajes de hasta
4000 caracteres (cortando entre secciones) y el archivo mismo como documento.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\telegram_texto_largo.py archivo.md
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(r"C:\dato-mata-gato-bot\.env"))
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ["TELEGRAM_ALLOWED_CHAT_IDS"].split(",")[0].strip()
URL = f"https://api.telegram.org/bot{TOKEN}"

archivo = Path(sys.argv[1])
texto = archivo.read_text(encoding="utf-8")
trozos, actual = [], ""
for bloque in texto.split("\n\n"):
    if len(actual) + len(bloque) + 2 > 4000 and actual:
        trozos.append(actual)
        actual = ""
    actual += bloque + "\n\n"
trozos.append(actual)
for t in trozos:
    r = requests.post(f"{URL}/sendMessage", data={"chat_id": CHAT, "text": t.strip(),
                                                  "disable_web_page_preview": "true"}, timeout=30)
    print("mensaje", r.status_code, r.json().get("ok"))
with open(archivo, "rb") as f:
    r = requests.post(f"{URL}/sendDocument", data={"chat_id": CHAT}, files={"document": f}, timeout=60)
print("documento", r.status_code, r.json().get("ok"))
