# utils/paths.py
import sys
import os
from pathlib import Path


def get_user_data_dir() -> Path:
    """Return the conventional per-user application-data directory."""
    home = Path.home()
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
    if sys.platform == "darwin":
        return home / "Library" / "Application Support"
    return Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))


def get_bundle_dir() -> Path:
    """Return the base directory for bundled read-only assets (supports PyInstaller frozen runtime)."""
    if getattr(sys, 'frozen', False):
        return Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


def get_paths():
    """
    Returns (install_dir, writable_data_dir).
    - If running as installed EXE (sys.frozen is True):
        install_dir = Path(sys.executable).parent
        writable_data_dir = get_user_data_dir() / "StudentManagementSystem"
    - If running from source:
        project_root = Path(__file__).resolve().parent.parent
        install_dir = project_root
        writable_data_dir = project_root
    """
    if getattr(sys, 'frozen', False):
        install_dir = Path(sys.executable).parent
        writable_data_dir = get_user_data_dir() / "StudentManagementSystem"
    else:
        # File is at utils/paths.py, so parent.parent is the project root
        project_root = Path(__file__).resolve().parent.parent
        install_dir = project_root
        writable_data_dir = project_root
    return install_dir, writable_data_dir


def get_asset_path(relative_name: str) -> Path:
    """
    Resolves an asset path checking bundle_dir, install_dir, and writable_dir.
    Works seamlessly in dev mode, PyInstaller onefolder, and PyInstaller onefile.
    """
    rel = Path(relative_name)
    # 1. Try bundle dir (works in dev and PyInstaller onefile _MEIPASS)
    candidate = get_bundle_dir() / rel
    if candidate.exists():
        return candidate
    # 2. Try install dir (for PyInstaller onedir next to executable)
    install_dir, writable_dir = get_paths()
    candidate = install_dir / rel
    if candidate.exists():
        return candidate
    # 3. Fallback to writable directory
    candidate = writable_dir / rel
    return candidate
