@echo off
chcp 65001 >nul
echo ======================================================================
echo   CHẠY TỰ ĐỘNG BỘ TEST POSTMAN API (NEWMAN) - VGA STORE
echo   Môn học: Kiểm chứng phần mềm
echo ======================================================================
echo.
echo Đang chạy kiểm thử API tự động với Newman...
echo.
npx newman run "C:\Users\TRONG\.gemini\antigravity-ide\scratch\vga-store\postman\VGA_Store.postman_collection.json" -e "C:\Users\TRONG\.gemini\antigravity-ide\scratch\vga-store\postman\VGA_Store.postman_environment.json"
echo.
echo ======================================================================
echo Hoàn thành kiểm thử! Bấm phím bất kỳ để thoát...
echo ======================================================================
pause >nul
