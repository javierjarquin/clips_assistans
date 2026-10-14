# POC de video completo con una voz de VoiceStudio (11/10/2026): genera <slug>
# con VOICESTUDIO_VOICE_ID_CRIMEN = <voz> solo para esta corrida (load_dotenv no
# pisa lo que ya está en el entorno) y con el ajuste B del gancho del .env.
# Espera a que no quede corriendo ningún proceso cuyo comando contenga <esperar>.
#   Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-File',
#     'C:\clip_assistance\tools\poc_video_voz.ps1','5f8ed11a','guion-tt-ed-gein-voznueva','poc_voz_nueva_ganchos'
param([string]$Voz, [string]$Slug, [string]$Esperar = "")

$py = "C:\dato-mata-gato-bot\.venv\Scripts\python.exe"
if ($Esperar) {
    while (Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match $Esperar }) { Start-Sleep 30 }
}
$env:VOICESTUDIO_VOICE_ID_CRIMEN = $Voz
$env:PYTHONIOENCODING = "utf-8"
$carpeta = "C:\Android_in\lotes\poc-voz-$Voz"
New-Item -ItemType Directory -Force $carpeta | Out-Null
& $py C:\clip_assistance\tools\poc_evidencia_video.py $Slug $carpeta 2>&1 | Out-File "$carpeta\_generacion.log" -Encoding utf8
