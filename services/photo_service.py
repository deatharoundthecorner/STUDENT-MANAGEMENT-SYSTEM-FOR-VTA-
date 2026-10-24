# services/photo_service.py
import os
import shutil
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from services.audit_service import AuditService

class PhotoService:
    def __init__(self):
        from utils.paths import get_paths
        self.install_dir, self.writable_dir = get_paths()
        self.base_dir = self.writable_dir
        self.photos_dir = self.base_dir / "student_photos"
        self.assets_dir = self.base_dir / "assets"
        self.default_avatar_path = self.assets_dir / "default_avatar.png"
        self.audit = AuditService()
        
        # Ensure directories exist
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        self.ensure_default_avatar()

    def ensure_default_avatar(self):
        """Generates a default avatar image if it does not exist."""
        if not self.default_avatar_path.exists():
            # Create a 200x200 pixel light gray image
            img = Image.new('RGB', (200, 200), color='#E0E4EC')
            draw = ImageDraw.Draw(img)
            # Draw a simple human silhouette (circle for head, ellipse for shoulders)
            # Head
            draw.ellipse([75, 40, 125, 90], fill='#7D8A9E')
            # Shoulders
            draw.ellipse([40, 110, 160, 210], fill='#7D8A9E')
            
            img.save(self.default_avatar_path)

    def save_photo(self, source_path_str: str, student_id_number: str) -> str:
        """
        Copies a photo from a source path to student_photos folder, 
        naming it using ID number and a timestamp. 
        Returns the relative path from the app root.
        """
        if not source_path_str:
            return ""

        source_path = Path(source_path_str)
        if not source_path.exists():
            return ""

        # Normalize student ID for file name (replace special characters with _)
        safe_id = "".join(c if c.isalnum() else "_" for c in student_id_number)
        timestamp = int(time.time())
        ext = source_path.suffix.lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            raise ValueError("Supported formats are JPG, JPEG, and PNG only.")

        new_filename = f"{safe_id}_{timestamp}{ext}"
        target_path = self.photos_dir / new_filename

        # Copy the file
        shutil.copy2(source_path, target_path)

        # Return relative path to app root so it is portable
        relative_path = f"student_photos/{new_filename}"
        self.audit.log_event("photo.add", summary={"path_hash": hash(relative_path)})
        return relative_path

    def delete_photo(self, relative_path: str):
        """Deletes the photo file specified by the relative path."""
        if not relative_path:
            return
        
        full_path = self.base_dir / relative_path
        if full_path.exists() and full_path.is_file():
            # Ensure it is actually inside the student_photos directory for safety
            if self.photos_dir.resolve() in full_path.resolve().parents:
                try:
                    os.remove(full_path)
                    self.audit.log_event("photo.remove", summary={"path_hash": hash(relative_path)})
                except OSError as e:
                    print(f"Error deleting photo file {full_path}: {e}")

    def get_absolute_path(self, relative_path: str) -> str:
        """Returns absolute path of a photo or default avatar if relative path is missing/invalid."""
        if not relative_path:
            return str(self.default_avatar_path)
        
        full_path = self.base_dir / relative_path
        if full_path.exists() and full_path.is_file():
            return str(full_path)
        
        return str(self.default_avatar_path)
        
    def get_photos_dir_path(self) -> str:
        """Returns the absolute path of the photos directory."""
        return str(self.photos_dir.resolve())
