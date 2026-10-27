@echo off
chcp 65001 >nul
cd /d "%~dp0"
title KIEM THU TU DONG POSTMAN API - VGA STORE
echo ======================================================================
echo   KIEM THU TU DONG POSTMAN API (NEWMAN) - VGA STORE
echo   Mon hoc: Kiem chung phan mem
echo ======================================================================
echo.
echo Dang chay kiem thu API tu dong voi Newman...
echo.
npx -y newman run "postman\VGA_Store.postman_collection.json" -e "postman\VGA_Store.postman_environment.json"
echo.
echo ======================================================================
echo Hoan thanh kiem thu!
echo ======================================================================
pause
