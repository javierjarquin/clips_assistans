# Prueba A/B de la etiqueta de IA en TikTok (11/10/2026): el mismo video de
# Ed Gein (guion, evidencia e imágenes idénticos) pero con la voz de Javier
# (perfil 95e2570b) en vez de Fish 3. Espera a que termine la tanda (por PID)
# para no pelear por VoiceStudio.
#
#   Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-File',
#     'C:\clip_assistance\tools\ab_voz_javier.ps1','<PID a esperar>'
param([int]$EsperarPid)

$py = "C:\dato-mata-gato-bot\.venv\Scripts\python.exe"
while (Get-Process -Id $EsperarPid -ErrorAction SilentlyContinue) { Start-Sleep 60 }

$origen = "C:\Android_in\guion-tt-ed-gein"
$slug = "guion-tt-ed-gein-vozjavier"
$destino = "C:\Android_in\$slug"
New-Item -ItemType Directory -Force $destino | Out-Null
Copy-Item "$origen\*" $destino -Recurse -Force

# load_dotenv no pisa lo que ya está en el entorno: así solo esta corrida usa
# la voz de Javier y el .env de producción queda igual.
$env:VOICESTUDIO_VOICE_ID_CRIMEN = "95e2570b"
# El de Fish 3 se hizo antes del ajuste B del gancho: para que solo cambie la
# voz, aquí se apaga (un espacio: con "" PowerShell borra la variable y el .env
# la volvería a poner).
$env:VOICESTUDIO_GANCHO_VELOCIDAD = " "
$env:VOICESTUDIO_GANCHO_GUIDANCE = " "
$env:PYTHONIOENCODING = "utf-8"
$carpeta = "C:\Android_in\lotes\2026-10-11-ab-voz"
New-Item -ItemType Directory -Force $carpeta | Out-Null
& $py C:\clip_assistance\tools\poc_evidencia_video.py $slug $carpeta 2>&1 |
    Out-File "$carpeta\_generacion.log" -Encoding utf8
& $py C:\clip_assistance\tools\telegram_enviar.py ("Prueba A/B lista: Ed Gein con TU voz (mismo guion e imagenes que el de Fish 3). " +
    "Sube los dos y fijate cual sale con la etiqueta de IA. Carpeta: $carpeta")
