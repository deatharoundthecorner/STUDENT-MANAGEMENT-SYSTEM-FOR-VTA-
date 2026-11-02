# -*- mode: python ; coding: utf-8 -*-
# StudentManagementSystem_phase48.spec
# Phase 48 Release Candidate v1.1.1 Packaging Specification
# Optimized PySide6 packaging with security and offline dependencies

from pathlib import Path
from PyInstaller.utils.hooks import collect_all

project_root = Path(SPECPATH).resolve()

datas = [
    (str(project_root / 'assets'), 'assets'),
]
binaries = []
hiddenimports = []

# Collect security and database runtime packages
for package in ('shiboken6', 'argon2', 'argon2_cffi_bindings', 'bcrypt'):
    tmp_ret = collect_all(package)
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

# Collect PySide6 with strict filtering of unused large modules
pyside_ret = collect_all('PySide6')

unused_bin_keywords = (
    'webengine', 'quick', 'qml', 'designer', '3d',
    'sensors', 'positioning', 'bluetooth', 'nfc',
    'spatialaudio', 'virtualkeyboard', 'multimedia',
    'avcodec', 'avformat', 'avutil', 'swresample', 'swscale', 'pdf'
)

for b in pyside_ret[1]:
    name = Path(b[0]).name.lower()
    if not any(k in name for k in unused_bin_keywords):
        binaries.append(b)

for d in pyside_ret[0]:
    src = str(d[0]).lower()
    if not any(k in src for k in ('webengine', 'qml', 'translations')):
        datas.append(d)

for h in pyside_ret[2]:
    h_lower = h.lower()
    if not any(k in h_lower for k in unused_bin_keywords):
        hiddenimports.append(h)

a = Analysis(
    [str(project_root / 'main.py')],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineQuick',
        'PySide6.QtQuick',
        'PySide6.QtQuickWidgets',
        'PySide6.QtQml',
        'PySide6.QtDesigner',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DExtras',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtSensors',
        'PySide6.QtPositioning',
        'PySide6.QtBluetooth',
        'PySide6.QtNfc',
        'PySide6.QtSpatialAudio',
        'PySide6.QtTest',
        'PySide6.QtVirtualKeyboard',
        'tkinter',
        'unittest',
    ],
    noarchive=False,
    optimize=0,
)

# Additional cleanup on auto-detected binaries in Analysis
a.binaries = [
    b for b in a.binaries
    if not any(k in Path(b[0]).name.lower() for k in unused_bin_keywords)
]

a.datas = [
    d for d in a.datas
    if not any(k in str(d[0]).lower() for k in ('webengine', 'qml', 'translations'))
]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StudentManagementSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'assets' / 'branding' / 'app_icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='StudentManagementSystem',
)
