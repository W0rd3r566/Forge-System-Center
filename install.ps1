$ErrorActionPreference = 'Stop'
$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Get-Command py -ErrorAction SilentlyContinue
if ($Python) {
    $BasePython = 'py'
} else {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python) { throw 'Python 3.10+ is required. Install Python and enable it in PATH.' }
    $BasePython = 'python'
}
$VersionCheck = @"
import sys
print(sys.version.split()[0])
raise SystemExit(0 if sys.version_info >= (3, 10) else 1)
"@
if ($BasePython -eq 'py') { $VersionOutput = & py -3 -c $VersionCheck } else { $VersionOutput = & python -c $VersionCheck }
if ($LASTEXITCODE -ne 0) { throw "Forge requires Python 3.10 or newer. Detected: $VersionOutput" }
if (-not (Test-Path "$AppDir\.venv\Scripts\python.exe")) {
    if ($BasePython -eq 'py') { & py -3 -m venv "$AppDir\.venv" } else { & python -m venv "$AppDir\.venv" }
}
$VenvPython = "$AppDir\.venv\Scripts\python.exe"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r "$AppDir\requirements.txt"
& $VenvPython -c "import PySide6, psutil; print('PySide6', PySide6.__version__); print('psutil', psutil.__version__)"
$StartMenu = [Environment]::GetFolderPath('Programs')
$ShortcutPath = Join-Path $StartMenu 'Forge System Center.lnk'
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $VenvPython
$Shortcut.Arguments = "`"$AppDir\run.py`""
$Shortcut.WorkingDirectory = $AppDir
$Shortcut.Description = 'Forge local desktop system center'
$Shortcut.Save()
Write-Host "Forge installed. Start it from the Start menu or run run.bat." -ForegroundColor Green
