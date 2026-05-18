@echo off
title BihiApp OS v4.0 — HTTPS
cd /d "C:\Users\Latifa\Desktop\claude project\bihibot-app\backend"
echo.
echo  BihiApp OS v4.0 — HTTPS MODE
echo  Voice Live enabled
echo  https://localhost:8000
echo.
start "" "https://localhost:8000"
C:\Python313\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem --reload
pause
