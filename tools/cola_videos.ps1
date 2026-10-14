# Espera a que termine otra tanda (por PID), genera la siguiente y avisa por
# Telegram cuando acaba. VoiceStudio sintetiza una voz a la vez: dos tandas en
# paralelo se estorban y tardan más que una tras otra.
#
#   Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-File',
#     'C:\clip_assistance\tools\cola_videos.ps1','<PID a esperar>','<carpeta>','slug1','slug2',...
param([int]$EsperarPid, [string]$Carpeta, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Slugs)

$py = "C:\dato-mata-gato-bot\.venv\Scripts\python.exe"
while (Get-Process -Id $EsperarPid -ErrorAction SilentlyContinue) { Start-Sleep 60 }

& powershell -NoProfile -ExecutionPolicy Bypass -File C:\clip_assistance\tools\correr_videos.ps1 $Carpeta @Slugs

$log = Get-Content "$Carpeta\_generacion.log" -Encoding utf8 -ErrorAction SilentlyContinue
$ok = @($log | Select-String "^OK ").Count
$fallo = @($log | Select-String "^FALL").Count
$texto = "Termine la tanda de videos de Cancun ($($Slugs.Count) guiones).`n" +
         "Listos en total en la carpeta: $ok   Fallidos: $fallo`n" +
         "Carpeta: $Carpeta`n" +
         "Cada video ya te llego por separado. Revisa sobre todo nombres y fechas."
& $py C:\clip_assistance\tools\telegram_enviar.py $texto
