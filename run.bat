@echo off
setlocal
if not exist "%~dp0.venv\Scripts\python.exe" (
  echo Forge is not installed. Run install.ps1 from PowerShell first.
  pause
  exit /b 1
)
"%~dp0.venv\Scripts\python.exe" "%~dp0run.py" %*
