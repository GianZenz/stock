param(
  [string]$Name = "StockAdvisor-Web",
  [string]$Icon = ""
)

Write-Host "Installing PyInstaller (if needed)..."
python -m pip install --upgrade pip pyinstaller | Out-Null

$addData = "stock/web/templates;stock/web/templates"

$iconArg = ""
if ($Icon -and (Test-Path $Icon)) { $iconArg = "--icon `"$Icon`"" }

Write-Host "Building single-file EXE..."
pyinstaller --noconfirm --clean --onefile `
  --name $Name `
  --add-data "$addData" `
  $iconArg `
  run_web.py

Write-Host "Done. EXE at dist\$Name.exe"

