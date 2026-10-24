@echo off
echo ===================================================
echo   Building Student Management System to EXE
echo ===================================================

if exist student_management_system (
echo Unexpected duplicate source tree detected: student_management_system
exit /b 1
)

python -m pip install --upgrade pip
python -m pip install PySide6 shiboken6 PyInstaller pandas openpyxl reportlab argon2-cffi bcrypt pillow

python -c "import PySide6; print('PySide6 OK')" || (
echo PySide6 is not installed correctly. Build stopped.
pause
exit /b 1
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

python -m PyInstaller --clean StudentManagementSystem.spec

echo.
echo Build completed.
echo Final EXE:
echo dist\StudentManagementSystem\StudentManagementSystem.exe
pause
