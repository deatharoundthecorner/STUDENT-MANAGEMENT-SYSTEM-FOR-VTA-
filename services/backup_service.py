# services/backup_service.py
import os
import shutil
import sqlite3
import stat
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from database.db import DatabaseManager
from services.audit_service import AuditService


class BackupService:
    def __init__(self):
        from utils.paths import get_paths
        self.install_dir, self.writable_dir = get_paths()
        self.base_dir = self.writable_dir
        self.backups_dir = self.base_dir / "backups"
        self.photos_dir = self.base_dir / "student_photos"
        self.db_manager = DatabaseManager()
        self.audit = AuditService()
        
        # Ensure backups folder exists
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> tuple:
        """
        Creates a ZIP backup containing the SQLite DB and student_photos folder.
        Uses SQLite Online Backup API to ensure atomic snapshot consistency.
        Validates snapshot integrity with PRAGMA integrity_check before archiving.
        Returns a tuple of (bool: success, str: backup_path or error_message).
        """
        try:
            db_path = self.db_manager.get_db_path()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.zip"
            backup_path = self.backups_dir / backup_filename
            counter = 1
            while backup_path.exists():
                backup_filename = f"backup_{timestamp}_{counter}.zip"
                backup_path = self.backups_dir / backup_filename
                counter += 1

            if not db_path.exists():
                return False, "Database file does not exist yet."

            with tempfile.TemporaryDirectory(dir=self.backups_dir) as temp_dir:
                staging_dir = Path(temp_dir)
                snapshot_path = staging_dir / db_path.name
                
                # 1. Use SQLite Online Backup API to create point-in-time snapshot
                source = sqlite3.connect(str(db_path))
                snapshot = sqlite3.connect(str(snapshot_path))
                try:
                    source.backup(snapshot)
                finally:
                    snapshot.close()
                    source.close()

                # 2. Check snapshot integrity before including in archive
                check_conn = sqlite3.connect(str(snapshot_path))
                try:
                    integrity_res = check_conn.execute("PRAGMA integrity_check").fetchone()
                    integrity = integrity_res[0] if integrity_res else "unknown"
                finally:
                    check_conn.close()

                if integrity != "ok":
                    raise ValueError(f"Snapshot integrity check failed: {integrity}")

                # 3. Write to temporary zip file first, then atomically move to final path
                temp_zip_path = staging_dir / backup_filename
                with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(snapshot_path, arcname=db_path.name)

                    if self.photos_dir.exists():
                        for file_path in self.photos_dir.rglob('*'):
                            if file_path.is_file() and not file_path.is_symlink():
                                relative_photo_path = file_path.relative_to(self.photos_dir)
                                zipf.write(
                                    file_path,
                                    arcname=Path('student_photos') / relative_photo_path,
                                )

                # Atomically move finished, verified zip to final destination
                shutil.move(str(temp_zip_path), str(backup_path))
            
            self.audit.log_event("backup.create", summary={"result": "success", "filename": backup_filename})
            return True, str(backup_path.resolve())
        except Exception as e:
            return False, f"Failed to create backup: {str(e)}"

    def list_backups(self) -> list:
        """Scans the backups directory and returns list of details about backups."""
        backups = []
        if not self.backups_dir.exists():
            return backups
            
        for file in self.backups_dir.glob("*.zip"):
            stats = file.stat()
            size_mb = stats.st_size / (1024 * 1024)
            creation_time = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            backups.append({
                "filename": file.name,
                "path": str(file.resolve()),
                "size": f"{size_mb:.2f} MB",
                "date": creation_time
            })
            
        # Return sorted by date descending
        backups.sort(key=lambda x: x["date"], reverse=True)
        return backups

    def restore_backup(self, backup_zip_path_str: str) -> tuple:
        """
        Restores database and photos from a ZIP archive with atomic rollback protection.
        Closes all active database connections before replacement to prevent Windows file locks.
        Returns a tuple of (bool: success, str: message).
        """
        try:
            backup_path = Path(backup_zip_path_str)
            if not backup_path.exists():
                return False, "Backup file not found."

            db_path = self.db_manager.get_db_path()
            self.backups_dir.mkdir(parents=True, exist_ok=True)

            with tempfile.TemporaryDirectory(dir=self.backups_dir) as temp_dir:
                staging_dir = Path(temp_dir)
                staged_db = staging_dir / db_path.name
                staged_photos = staging_dir / 'student_photos'
                staged_photos.mkdir(parents=True, exist_ok=True)

                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    members = zipf.infolist()
                    if db_path.name not in {member.filename for member in members}:
                        raise ValueError("Invalid backup file: Missing database file.")

                    for member in members:
                        member_path = PurePosixPath(member.filename)
                        if member_path.is_absolute() or '..' in member_path.parts:
                            raise ValueError("Invalid backup file: Unsafe archive path.")
                        if stat.S_ISLNK(member.external_attr >> 16):
                            raise ValueError("Invalid backup file: Symbolic links are not allowed.")
                        if member.filename != db_path.name and not member.filename.startswith('student_photos/'):
                            raise ValueError("Invalid backup file: Unexpected archive entry.")
                        if member.is_dir():
                            continue

                        destination = staged_db if member.filename == db_path.name else staging_dir / member_path
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        with zipf.open(member) as source, destination.open('wb') as target:
                            shutil.copyfileobj(source, target)

                connection = sqlite3.connect(str(staged_db))
                try:
                    integrity_res = connection.execute('PRAGMA integrity_check').fetchone()
                    integrity = integrity_res[0] if integrity_res else 'unknown'
                finally:
                    connection.close()
                if integrity != 'ok':
                    raise ValueError(f'Invalid backup database: integrity check returned {integrity!r}.')

                # Ensure all open connections are closed before file manipulation on Windows
                self.db_manager.close_all_connections()

                rollback_db = db_path.parent / f'.{db_path.name}.restore-backup'
                rollback_wal = db_path.parent / f'.{db_path.name}-wal.restore-backup'
                rollback_shm = db_path.parent / f'.{db_path.name}-shm.restore-backup'
                live_wal = db_path.parent / f'{db_path.name}-wal'
                live_shm = db_path.parent / f'{db_path.name}-shm'
                rollback_photos = self.photos_dir.parent / '.student_photos.restore-backup'
                
                had_db = db_path.exists()
                had_wal = live_wal.exists()
                had_shm = live_shm.exists()
                had_photos = self.photos_dir.exists()

                for f in (rollback_db, rollback_wal, rollback_shm):
                    if f.exists():
                        f.unlink()
                if rollback_photos.exists():
                    shutil.rmtree(rollback_photos)

                try:
                    if had_db:
                        shutil.copy2(db_path, rollback_db)
                    if had_wal:
                        shutil.copy2(live_wal, rollback_wal)
                        live_wal.unlink()
                    if had_shm:
                        shutil.copy2(live_shm, rollback_shm)
                        live_shm.unlink()
                    if had_photos:
                        shutil.copytree(self.photos_dir, rollback_photos)

                    db_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(staged_db, db_path)
                    
                    if self.photos_dir.exists():
                        shutil.rmtree(self.photos_dir)
                    shutil.copytree(staged_photos, self.photos_dir)
                except Exception:
                    # Rollback on failure
                    if rollback_db.exists():
                        shutil.copy2(rollback_db, db_path)
                    elif not had_db and db_path.exists():
                        db_path.unlink()
                    if rollback_wal.exists():
                        shutil.copy2(rollback_wal, live_wal)
                    if rollback_shm.exists():
                        shutil.copy2(rollback_shm, live_shm)
                    if rollback_photos.exists():
                        if self.photos_dir.exists():
                            shutil.rmtree(self.photos_dir)
                        shutil.copytree(rollback_photos, self.photos_dir)
                    elif not had_photos and self.photos_dir.exists():
                        shutil.rmtree(self.photos_dir)
                    raise
                finally:
                    for f in (rollback_db, rollback_wal, rollback_shm):
                        if f.exists():
                            try:
                                f.unlink()
                            except Exception:
                                pass
                    if rollback_photos.exists():
                        try:
                            shutil.rmtree(rollback_photos)
                        except Exception:
                            pass

            self.audit.log_event("backup.restore", summary={"result": "success"})
            return True, "System restored successfully. Please reload/restart data views."
                
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
