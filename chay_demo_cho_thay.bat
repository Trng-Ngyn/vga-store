@echo off
chcp 65001 >nul
echo ======================================================================
echo   DEMO BÀI TẬP LỚN MÔN KIỂM CHỨNG PHẦN MỀM (VGA STORE)
echo ======================================================================
echo.
echo [1] Đang mở bảng Jira dự án trên trình duyệt...
start https://kiemchungphanmem.atlassian.net/jira/software/projects/KAN/boards/1

echo [2] Đang mở thư mục chứa 2 file Postman Collection trong Downloads...
explorer C:\Users\TRONG\Downloads

echo [3] Đang mở thư mục mã nguồn dự án...
explorer C:\Users\TRONG\.gemini\antigravity-ide\scratch\vga-store

echo.
echo ======================================================================
echo HƯỚNG DẪN TRÌNH BÀY CHO THẦY XEM:
echo 1. Trên Jira: Cho thầy thấy bảng Kanban phân chia 18 tasks cho 6 người.
echo    Ba task KAN-3, KAN-4, KAN-5 của bạn đã hoàn thành (cột Done).
echo.
echo 2. Trên Postman: Mở Postman, bấm nút 'Import' và chọn 2 file:
echo    - VGA_Store.postman_collection.json
echo    - VGA_Store.postman_environment.json
echo    (Đã để sẵn trong Downloads của bạn).
echo.
echo 3. Sau đó chọn Environment 'VGA Store - Local Environment' rồi bấm Run
echo    để thầy thấy toàn bộ kịch bản kiểm thử API chạy tự động.
echo ======================================================================
echo.
pause
