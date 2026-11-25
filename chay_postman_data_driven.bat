@echo off
chcp 65001 >nul
cd /d "%~dp0"
title KIEM THU HUONG DU LIEU (DATA-DRIVEN TESTING) - POSTMAN NEWMAN
echo ======================================================================
echo   DATA-DRIVEN TESTING (DDT) VOI POSTMAN & NEWMAN
echo   Du an: VGA Store - Mon hoc: Kiem chung phan mem
echo ======================================================================
echo.
echo Dang doc file du lieu kiem thu: postman\data_login_test.csv...
echo.
npx -y newman run "postman\VGA_Store.postman_collection.json" -e "postman\VGA_Store.postman_environment.json" -d "postman\data_login_test.csv"
echo.
echo ======================================================================
echo Hoan thanh kiem thu huong du lieu (Data-Driven Testing)!
echo ======================================================================
pause
