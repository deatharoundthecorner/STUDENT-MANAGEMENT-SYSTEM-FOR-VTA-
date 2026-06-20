@echo off
echo ===================================================
echo   Building Student Management System to EXE
echo ===================================================

python -m pip install --upgrade pip
python -m pip install PySide6 shiboken6 PyInstaller pandas openpyxl reportlab bcrypt pillow

python -c "import PySide6; print('PySide6 OK')" || (
echo PySide6 is not installed correctly. Build stopped.
pause
exit /b 1
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist StudentManagementSystem.spec del StudentManagementSystem.spec

python -m PyInstaller ^
--noconsole ^
--onedir ^
--clean ^
--name StudentManagementSystem ^
--collect-all PySide6 ^
--collect-all shiboken6 ^
main.py

echo.
echo Build completed.
echo Final EXE:
echo dist\StudentManagementSystem\StudentManagementSystem.exe
pause
