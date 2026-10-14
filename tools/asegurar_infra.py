"""Docker Desktop y VoiceStudio arriba antes de cada video (13/10/2026).

Usa la misma revisión que la fábrica (`fabrica.asegurar_infra`): si VoiceStudio
no responde, arranca Docker Desktop si hace falta y luego el contenedor. Nace
de la comparación de flujos del 13/10: Docker se apagó a media corrida de
correr_videos.ps1 y los dos videos fallaron en la voz.

Sale con 0 si todo está arriba; con 1 (y aviso por Telegram) si no se pudo.

    C:\\dato-mata-gato-bot\\.venv\\Scripts\\python.exe tools\\asegurar_infra.py [slug]
"""

import sys

sys.path.insert(0, r"C:\dato-mata-gato-bot\src")

from dotenv import load_dotenv  # noqa: E402

load_dotenv(r"C:\dato-mata-gato-bot\.env")

from dato_mata_gato_bot import fabrica  # noqa: E402

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    slug = sys.argv[1] if len(sys.argv) > 1 else ""
    ya_estaba = fabrica._voicestudio_responde()
    problema = fabrica.asegurar_infra()
    if problema:
        print(f"INFRA FALLÓ: {problema}")
        fabrica.telegram(f"⚠️ No pude levantar la voz antes de {slug or 'el video'}: {problema}")
        sys.exit(1)
    print("infra ok" if ya_estaba else "infra ok (Docker/VoiceStudio estaban caídos y se levantaron)")
