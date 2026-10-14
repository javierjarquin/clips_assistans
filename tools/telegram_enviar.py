"""Manda un mensaje (y opcionalmente un audio o video) al chat del bot.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\telegram_enviar.py "texto" [archivo]
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(r"C:\dato-mata-gato-bot\.env"))
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ["TELEGRAM_ALLOWED_CHAT_IDS"].split(",")[0].strip()
texto = sys.argv[1]
archivo = Path(sys.argv[2]) if len(sys.argv) > 2 else None
url = f"https://api.telegram.org/bot{TOKEN}"
if archivo is None:
    r = requests.post(f"{url}/sendMessage", data={"chat_id": CHAT, "text": texto}, timeout=30)
else:
    metodo, campo = (("sendVideo", "video") if archivo.suffix == ".mp4"
                     else ("sendAudio", "audio"))
    with open(archivo, "rb") as f:
        r = requests.post(f"{url}/{metodo}", data={"chat_id": CHAT, "caption": texto},
                          files={campo: f}, timeout=300)
print(r.status_code, r.json().get("ok"))
