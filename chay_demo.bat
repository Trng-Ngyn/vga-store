@echo off
chcp 65001 >nul
cd /d "%~dp0"
title KHOI DONG DEMO HE THONG - VGA STORE
echo ======================================================================
echo   HE THONG KIEM CHUNG PHAN MEM - VGA STORE
echo ======================================================================
echo.

echo [1] Dang mo Website ban hang (User Frontend): http://localhost:5173
start http://localhost:5173

echo [2] Dang mo Trang quan tri (Admin Dashboard): http://localhost:5174/login
start http://localhost:5174/login

echo [3] Dang mo GitHub Actions (CI/CD Pipeline):
start https://github.com/Trng-Ngyn/vga-store/actions

echo [4] Dang mo Bang quan ly cong viec Jira:
start https://kiemchungphanmem.atlassian.net

echo [5] Dang mo thu muc Postman Collection:
explorer C:\Users\TRONG\.gemini\antigravity-ide\scratch\vga-store\postman

echo.
echo ======================================================================
echo TONG HOP TAI KHOAN VA TIEN DO:
echo - Website User:   http://localhost:5173
echo - Website Admin:  http://localhost:5174 (admin / 123)
echo - Backend API:    http://localhost:8080
echo - CI/CD GitHub:   Xanh 100%% (4/4 quy trinh: CI, Qodana, CodeceptJS, Docker)
echo - Postman API:    100%% PASS (8 kich ban kiem thu)
echo - Jira Kanban:    20 task hoan thanh
echo ======================================================================
echo.
pause

