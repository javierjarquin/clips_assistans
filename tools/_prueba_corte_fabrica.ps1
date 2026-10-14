# Prueba de corte (12/10/2026): espera a que la fábrica esté renderizando,
# deja correr 3 minutos y mata TODO el árbol del ciclo, como un apagón.
$deadline = (Get-Date).AddMinutes(40)
while ((Get-Date) -lt $deadline) {
    $hijo = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -match 'dato_mata_gato_bot.fabrica video piloto-cercania' }
    if ($hijo) { break }
    Start-Sleep 20
}
if (-not $hijo) { "no arrancó ningún render en 40 min"; exit 1 }
"render detectado $(Get-Date -Format HH:mm:ss): $(($hijo | Select-Object -First 1).CommandLine.Split(' ')[-1])"
Start-Sleep 180
$ciclo = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python' -and $_.CommandLine -match 'fabrica.py" ciclo' -and $_.ExecutablePath -match 'venv' }
foreach ($p in $ciclo) { taskkill /T /F /PID $p.ProcessId | Out-Null; "matado árbol del ciclo PID $($p.ProcessId) a las $(Get-Date -Format HH:mm:ss)" }
