@echo off
REM Avvio semplice dell'app Web in italiano
REM 1) Verifica Python
where python >nul 2>&1
if %errorlevel% neq 0 (
  where py >nul 2>&1
  if %errorlevel% neq 0 (
    echo [ERRORE] Python non trovato. Installa Python da https://www.python.org/downloads/ e riprova.
    pause
    exit /b 1
  ) else (
    set PY=py
  )
) else (
  set PY=python
)

REM 2) Avvio server web (auto-installa dipendenze se mancano)
%PY% -m stock.web --host 127.0.0.1 --port 8000 --lang it

REM 3) Apri browser (se il comando sopra resta in esecuzione, aprire manualmente http://127.0.0.1:8000/)
REM start "" http://127.0.0.1:8000/
