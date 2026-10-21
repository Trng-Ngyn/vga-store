@echo off
chcp 65001 >nul
cd /d "%~dp0"
title KHOI DONG DOCKER COMPOSE - VGA STORE
echo ======================================================================
echo   DOCKER COMPOSE: KHOI DONG TOAN BO 4 CONTAINER DONG BO
echo ======================================================================
echo.


set "PATH=C:\Users\TRONG\AppData\Local\Programs\DockerDesktop\resources\bin;%PATH%"

echo [1] Dang kiem tra ket noi Docker Engine...
docker --version
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Docker. Vui long mo Docker Desktop truoc!
    pause
    exit /b 1
)

echo.
echo [2] Dang khoi chay 4 container theo docker-compose.yml...
docker compose up -d

echo.
echo [3] Danh sach cac container dang hoat dong:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ======================================================================
echo HE THONG DA KHOI CHAY HOAN TAT TRONG DOCKER:
echo - Website Khach hang (User):  http://localhost:5173
echo - Website Quan tri (Admin):   http://localhost:5174
echo - Backend API Spring Boot:    http://localhost:8080
echo - Database PostgreSQL:        localhost:5433
echo ======================================================================
echo.
pause
