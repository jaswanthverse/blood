@echo off
cd /d C:\Users\jaswa\bloodbank_system
call C:\Users\jaswa\venv\Scripts\activate.bat
start "" cmd /c python manage.py runserver
timeout /t 3 /nobreak >nul
start http://127.0.0.1:8000/