# Install and Release Guide

## Prerequisites for developers

- Windows 10 or Windows 11 x64
- Python 3.11+ (for building only)
- PyInstaller
- Inno Setup 6
- Git

## Build steps

1. Open PowerShell in the project root.
2. Install Python requirements:
   `pip install -r requirements.txt`
3. Build the project:
   `powershell -ExecutionPolicy Bypass -File installer\build_release.ps1`
4. The installer output is written to `installer_output\`.

## Notes

- This project is intended for local-office desktop use.
- The app must not rely on Python being installed on the target computer.
- The installer packages an app directory and is created in `--onedir` mode.
