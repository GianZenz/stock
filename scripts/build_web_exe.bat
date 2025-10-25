@echo off
set NAME=StockAdvisor-Web
echo Installing PyInstaller...
python -m pip install --upgrade pip pyinstaller >nul 2>&1
echo Building EXE...
pyinstaller --noconfirm --clean --onefile --name %NAME% --add-data "stock/web/templates;stock/web/templates" run_web.py
echo Done. Find the executable in dist\%NAME%.exe

