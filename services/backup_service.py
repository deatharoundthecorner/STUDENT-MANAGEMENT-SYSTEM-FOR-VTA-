# services/backup_service.py
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from database.db import DatabaseManager

class BackupService:
    def __init__(self):
        import sys
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).resolve().parent.parent
        self.backups_dir = self.base_dir / "backups"
        self.photos_dir = self.base_dir / "student_photos"
        self.db_manager = DatabaseManager()
        
        # Ensure backups folder exists
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> tuple:
        """
        Creates a ZIP backup containing the SQLite DB and student_photos folder.
        Returns a tuple of (bool: success, str: backup_path or error_message).
        """
        try:
            db_path = self.db_manager.get_db_path()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.zip"
            backup_path = self.backups_dir / backup_filename

            # Temporarily close any active SQLite connections if possible, 
            # though standard sqlite3 handles file copies. We will read the db file directly.
            if not db_path.exists():
                return False, "Database file does not exist yet."

            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add database
                zipf.write(db_path, arcname=db_path.name)
                
                # Add all student photos
                if self.photos_dir.exists():
                    for root, dirs, files in os.walk(self.photos_dir):
                        for file in files:
                            file_path = Path(root) / file
                            # Arcname should be relative to the base directory (i.e. starts with student_photos/)
                            arcname = Path("student_photos") / file
                            zipf.write(file_path, arcname=arcname)
            
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
        Restores database and photos from a ZIP archive.
        Returns a tuple of (bool: success, str: message).
        """
        try:
            backup_path = Path(backup_zip_path_str)
            if not backup_path.exists():
                return False, "Backup file not found."

            db_path = self.db_manager.get_db_path()
            
            # Close active connections (by forcing garbage collection or just rely on overwrite)
            # Standard python sqlite3 allows replacing the file but we should be careful.
            
            # We will copy old files to temporary locations as rollback insurance
            temp_db = db_path.parent / (db_path.name + ".tmp")
            temp_photos = self.photos_dir.parent / "student_photos_tmp"
            
            rolled_back = False
            
            # Backup active files for safety
            if db_path.exists():
                shutil.copy2(db_path, temp_db)
            if self.photos_dir.exists():
                shutil.copytree(self.photos_dir, temp_photos, dirs_exist_ok=True)
                
            try:
                # Extract backup files
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    # Check list of files in zip to verify validity
                    namelist = zipf.namelist()
                    if db_path.name not in namelist:
                        raise ValueError("Invalid backup file: Missing database file.")

                    # Delete current photos to avoid orphaned files
                    if self.photos_dir.exists():
                        shutil.rmtree(self.photos_dir)
                    self.photos_dir.mkdir(parents=True, exist_ok=True)

                    # Extract files
                    for member in zipf.infolist():
                        if member.filename == db_path.name:
                            # Extract database file to its target path
                            with zipf.open(member) as source, open(db_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                        elif member.filename.startswith("student_photos/"):
                            # Extract photo files
                            zipf.extract(member, path=self.base_dir)
                            
                # Cleanup backups
                if temp_db.exists():
                    os.remove(temp_db)
                if temp_photos.exists():
                    shutil.rmtree(temp_photos)
                    
                return True, "System restored successfully. Please reload/restart data views."
                
            except Exception as inner_ex:
                # Rollback!
                if temp_db.exists():
                    if db_path.exists():
                        os.remove(db_path)
                    shutil.copy2(temp_db, db_path)
                    os.remove(temp_db)
                if temp_photos.exists():
                    if self.photos_dir.exists():
                        shutil.rmtree(self.photos_dir)
                    shutil.copytree(temp_photos, self.photos_dir, dirs_exist_ok=True)
                    shutil.rmtree(temp_photos)
                rolled_back = True
                raise inner_ex
                
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
