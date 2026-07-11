@echo off
rem Lanzador de la interfaz gráfica — doble clic y listo, no requiere poetry
cd /d "%~dp0"
start "" ".venv\Scripts\pythonw.exe" -m shorts_factory.gui.app
