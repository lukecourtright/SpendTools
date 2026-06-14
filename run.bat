@echo off
cd /d "%~dp0"
echo Starting SpendTools...
echo Open http://localhost:8000 in your browser.
echo Press Ctrl+C to stop.
python -m uvicorn main:app --port 8000
pause
