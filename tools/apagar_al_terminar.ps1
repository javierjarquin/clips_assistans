# Al terminar la fábrica piloto (12/10/2026, pedido de Javier): manda el
# resumen final por Telegram y apaga la PC 5 minutos después.
# Si a la hora límite no terminó, avisa y NO apaga (no se corta un video a medias).
#   Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass',
#     '-File','C:\clip_assistance\tools\apagar_al_terminar.ps1','piloto-cercania','21:00'
param([string]$Lote = "piloto-cercania", [string]$HoraLimite = "21:00", [switch]$Simular)

$py = "C:\dato-mata-gato-bot\.venv\Scripts\python.exe"
$tg = "C:\clip_assistance\tools\telegram_enviar.py"
$resumenPy = "C:\clip_assistance\tools\resumen_fabrica.py"
$estado = "C:\Android_in\fabrica\$Lote\estado.json"
$limite = [datetime]::ParseExact($HoraLimite, "HH:mm", $null)
if ($limite -lt (Get-Date)) { $limite = $limite.AddDays(1) }
$env:PYTHONIOENCODING = "utf-8"

while ((Get-Date) -lt $limite) {
    $e = Get-Content $estado -Raw -Encoding utf8 | ConvertFrom-Json
    if ($e.terminado) { break }
    Start-Sleep 60
}
$e = Get-Content $estado -Raw -Encoding utf8 | ConvertFrom-Json
if (-not $e.terminado) {
    & $py $tg "La fabrica $Lote no termino antes de las $HoraLimite. NO apague la PC para no cortar un video a medias. Sigue trabajando sola."
    exit 1
}

$resumen = & $py $resumenPy $Lote
if ($Simular) { "SIMULACION - mandaria:"; $resumen; "y apagaria en 5 min"; exit 0 }
& $py $tg ($resumen -join "`n")
shutdown /s /t 300 /c "Dato Mata Gato: piloto terminado. La PC se apaga en 5 minutos (cancelar: shutdown /a)."
