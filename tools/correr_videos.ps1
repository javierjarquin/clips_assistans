# Genera varios videos con evidencia, uno tras otro, como proceso independiente
# (las tareas lanzadas desde una sesión de Claude Code tienen límite de tiempo).
# Cada video avisa por Telegram al empezar y manda el video al terminar.
#
#   Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-File',
#     'C:\clip_assistance\tools\correr_videos.ps1','C:\Android_in\lotes\2026-10-05','slug1','slug2'
param([string]$Carpeta, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Slugs)

$py = "C:\dato-mata-gato-bot\.venv\Scripts\python.exe"
$log = "$Carpeta\_generacion.log"
New-Item -ItemType Directory -Force $Carpeta | Out-Null
$env:PYTHONIOENCODING = "utf-8"
# Prueba de voces (11/10/2026): Fish 3 y la voz nueva de Javier, una y una.
$lista = ($Slugs | ForEach-Object { "'$_'" }) -join ","
& $py -c "import sys; sys.path.insert(0, r'C:\dato-mata-gato-bot\src'); from dotenv import load_dotenv; load_dotenv(r'C:\dato-mata-gato-bot\.env'); from pathlib import Path; from dato_mata_gato_bot import lote_grande as l; print(l.repartir_voces(l.Plan(carpeta=Path(r'$Carpeta'), tareas=[(s, None) for s in [$lista]])))" 2>&1 |
    Out-File $log -Append -Encoding utf8
foreach ($slug in $Slugs) {
    "[$(Get-Date -Format HH:mm:ss)] === $slug ===" | Out-File $log -Append -Encoding utf8
    # Docker y VoiceStudio arriba antes de cada video (13/10/2026: Docker se
    # apagó a media corrida y los dos videos fallaron en la voz). Si no se
    # levantan, se para aquí: los que siguen fallarían igual.
    & $py C:\clip_assistance\tools\asegurar_infra.py $slug 2>&1 |
        Where-Object { "$_" -notmatch "FutureWarning|warnings.warn" } | Out-File $log -Append -Encoding utf8
    if ($LASTEXITCODE -ne 0) {
        "[$(Get-Date -Format HH:mm:ss)] === parado: la voz no levantó ===" | Out-File $log -Append -Encoding utf8
        break
    }
    & $py C:\clip_assistance\tools\poc_evidencia_video.py $slug $Carpeta 2>&1 |
        Where-Object { "$_" -notmatch "FutureWarning|warnings.warn" } | Out-File $log -Append -Encoding utf8
}
"[$(Get-Date -Format HH:mm:ss)] === fin ===" | Out-File $log -Append -Encoding utf8
