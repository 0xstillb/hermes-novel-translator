@REM Windows Setup Script — วางไว้ใน USB รันทีเดียว
@REM ดับเบิลคลิก หรือรันใน CMD: setup-windows.bat

@echo off
echo ========================================
echo   Hermes Novel Translator - Windows Setup
echo ========================================
echo.

:: 1. หา drive ของ USB
set USB_DRIVE=%~d0

:: 2. unzip ไปที่ home
echo [1/4] กำลังแตกไฟล์...
tar -xf "%USB_DRIVE%\hermes-novel-translator-pack.zip" -C "%USERPROFILE%" 2>nul
if errorlevel 1 (
    powershell -Command "Expand-Archive -Path '%USB_DRIVE%\hermes-novel-translator-pack.zip' -DestinationPath '%USERPROFILE%' -Force"
)

:: 3. สร้าง translator profile
echo [2/4] กำลังสร้าง Translator Profile...
hermes profile create translator --clone >nul 2>&1
hermes --profile translator config set model deepseek-v4-flash >nul 2>&1

:: 4. เช็คว่า skill โหลดหรือยัง
echo [3/4] ตรวจสอบ Skill...
hermes skills list | findstr "cn-th-novel-translation" >nul
if errorlevel 1 (
    echo WARNING: Skill not loaded. อาจต้อง restart Hermes (hermes quit)
    echo   Skill อยู่ที่: %USERPROFILE%\.hermes\skills\custom\cn-th-novel-translation\
    echo   ถ้ายังไม่ขึ้น ลอง: hermes skills scan
)

:: 5. เสร็จ
echo [4/4] เสร็จสมบูรณ์!
echo.
echo ========================================
echo   วิธีใช้:
echo     translator chat
echo.
echo   หรือ:
echo     hermes --profile translator
echo ========================================
pause
