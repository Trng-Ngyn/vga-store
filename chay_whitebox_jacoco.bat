@echo off
chcp 65001 >nul
cd /d "%~dp0backend\vgashop"
title KIEM THU HOP TRANG (WHITE-BOX TESTING) + JACOCO COVERAGE - VGA STORE
echo ======================================================================
echo   KIEM THU HOP TRANG (WHITE-BOX UNIT TEST & JACOCO CODE COVERAGE)
echo   Cong cu: JUnit 5 + Mockito + JaCoCo 0.8.12
echo ======================================================================
echo.
set "JACOCO_JAR=%USERPROFILE%\.m2\repository\org\jacoco\org.jacoco.agent\0.8.12\org.jacoco.agent-0.8.12-runtime.jar"
if exist "%JACOCO_JAR%" (
    set "MAVEN_OPTS=-javaagent:%JACOCO_JAR%=destfile=target/jacoco.exec"
)
call .\mvnw.cmd test
if %errorlevel% equ 0 (
    set "MAVEN_OPTS="
    call .\mvnw.cmd jacoco:report
    echo.
    echo ======================================================================
    echo   HOAN THANH! Dang mo bao cao do phu ma nguon (JaCoCo HTML Report)...
    echo ======================================================================
    start "" "target\site\jacoco\index.html"
) else (
    echo [LOI] Co loi khi chay Unit Test!
)
pause
