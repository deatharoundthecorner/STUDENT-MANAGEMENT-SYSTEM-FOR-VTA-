# Release Checklist

## Windows clean-machine verification

- Windows 10 x64
- Windows 11 x64
- Run installer without admin rights where possible
- First-run setup creates admin account
- Login works with strong password
- Student CRUD works
- Import spreadsheet works
- Export CSV/Excel/PDF works
- Backup and restore works
- Photo upload works
- Theme switch works
- Upgrade install preserves data
- Uninstall preserves user data unless explicitly selected

## Required release evidence

- Installer produced successfully
- Setup.exe runs without Python on target machine
- App starts from Start Menu shortcut
- Data remains in LocalAppData
- No shared SQLite database is used
- Clean canonical-source scanner reports for detect-secrets, Bandit, and pip-audit
- Duplicate-tree decision completed and archival mirror resolved before first public release
- Fresh PyInstaller build from the canonical root
- Inno Setup compiler available and installer compiled
- Clean Windows installation test completed
- Code-signing certificate available and applied before public distribution
