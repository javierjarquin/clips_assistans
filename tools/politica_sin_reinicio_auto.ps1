# Windows Update no reinicia solo mientras haya un usuario con sesión iniciada
# (14/10/2026). El 14/10 a las 03:31-03:34 tres reinicios de actualización
# tumbaron el bot y Docker a media madrugada, cuando la fábrica trabaja.
# Con esto Windows instala igual, pero el reinicio lo decide Javier.
# Requiere administrador:
#   Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-File','C:\clip_assistance\tools\politica_sin_reinicio_auto.ps1'
# Para deshacerlo: Remove-ItemProperty -Path $ruta -Name NoAutoRebootWithLoggedOnUsers
$ruta = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'
$salida = 'C:\clip_assistance\analisis\politica_sin_reinicio_auto.txt'
try {
    New-Item -Path $ruta -Force | Out-Null
    New-ItemProperty -Path $ruta -Name 'NoAutoRebootWithLoggedOnUsers' -Value 1 -PropertyType DWord -Force | Out-Null
    $v = (Get-ItemProperty $ruta).NoAutoRebootWithLoggedOnUsers
    "ok NoAutoRebootWithLoggedOnUsers=$v $(Get-Date -Format s)" | Out-File $salida -Encoding utf8
} catch {
    "error: $($_.Exception.Message)" | Out-File $salida -Encoding utf8
}
