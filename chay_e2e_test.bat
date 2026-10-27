@echo off
chcp 65001 >nul
cd /d "%~dp0"
title KIEM THU TU DONG E2E CODECEPTJS - VGA STORE
echo ======================================================================
echo   KIEM THU TU DONG E2E CODECEPTJS & PLAYWRIGHT - VGA STORE
echo   Mon hoc: Kiem chung phan mem
echo ======================================================================
echo.
echo Dang khoi dong trinh duyet Chrome va chay kiem thu E2E tu dong...
echo.
cd e2e-tests
npx codeceptjs run --steps
echo.
echo ======================================================================
echo Hoan thanh kiem thu E2E!
echo ======================================================================
pause
