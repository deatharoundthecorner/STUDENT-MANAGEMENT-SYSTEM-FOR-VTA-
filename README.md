# Student Management System (SMS) - Windows Offline Edition

A professional, offline Windows desktop application developed in Python with **PySide6** and **SQLite** for maintaining, importing, and reporting student academic, training, and placement records.

---

## 🔐 First-run administrator setup

The application does not ship with a default username or password. On first launch, create the administrator account with a strong password. Existing legacy accounts may be required to replace their password before normal access.

---

## 🚀 Installation & Running Locally

Follow these steps to run the application directly from source code:

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed on your Windows machine.

### 2. Install Python Dependencies
Open your command prompt (`cmd`) in the canonical project root directory and install the necessary libraries:

```bash
pip install -r requirements.txt
```

*Required packages include: `PySide6`, `pandas`, `openpyxl`, `reportlab`, `argon2-cffi`, `bcrypt` (legacy verification), `pillow`, and `pyinstaller`.*

### 3. Run the Application
Launch the system with:

```bash
python main.py
```

*Note: On first startup, the database file `student_records.db` and the asset/backup folders are automatically generated.*

---

## 📂 Core Workflows

### 1. Registering & Editing Students
- Navigate to **Add Student** in the sidebar.
- Provide the required **ID Number** and **Student Name**. The student ID must be unique.
- Choose a student photo (`.png`, `.jpg`, `.jpeg`). It will be automatically renamed and saved locally inside the `student_photos/` folder.
- Fill in academic statuses, OJT placements, and current job locations.
- Click **Save Student Record** to commit to the offline database.

### 2. Searching and Filtering Records
- Go to the **Student Records** page.
- Use the search bar to filter by name, ID number, contact number, OJT placement, or job company.
- Apply dropdown filters (such as Registered Year or completion levels) to isolate cohorts.
- Click **Reset** to clear active filters.

### 3. Data Imports (Excel & CSV)
- Go to the **Import Data** page.
- You can download a blank template structure by clicking **Download CSV Template** or **Download Excel Template**.
- Align your columns to match the template (e.g. `ID_NUMBER`, `NAME_OF_THE_STUDENT`, etc.). Case-insensitive mappings are fully supported.
- Click **Select File** to load your sheet. The system will load a **Top 10 rows Preview** so you can check alignment.
- Click **Process Data Import**. The system will report counts for:
  - **Successfully Imported**
  - **Skipped** (Students with IDs that already exist in the database, avoiding overrides)
  - **Failed** (Rows with missing IDs, missing names, or invalid phone numbers)
- Review row-by-row failures in the scrollable red warning log if any occur.

### 4. Data Exports (CSV, Excel, & PDF Reports)
- Navigate to **Export / Backup** from the sidebar.
- Click **Export to Excel** or **Export to CSV** to write the complete table to file.
- Click **Export Summary PDF** to write a landscape, formatted A4 PDF summary listing all students, counts, and primary attributes.
- To export an individual student's profile sheet with their photo, go to **Student Records** -> click **View** -> click **Export Profile PDF**.

### 5. Database Backup and Restore
- Navigate to **Export / Backup**.
- Click **Create Full Backup**. This generates a compressed timestamped ZIP file under `backups/` bundling the database (`student_records.db`) and the active `student_photos/` folder.
- To restore the system, look at the **Available Restoration Snapshots** table.
- Click **Restore Backup** on the target date. 
- *Caution: Restoring will overwrite active records with the backup state. Verify the rollback prompts before accepting.*

### 6. Theme Settings (Day & Night Mode)
- Switch between **Day Mode** and **Night Mode** at any time.
- To change themes, go to the **Settings** page -> look for the **Appearance Settings** section -> select your preferred theme in the dropdown.
- Alternatively, click the **Theme Toggle Button** (🌙/☀️) located at the bottom of the sidebar navigation to toggle themes instantly.
- The selected theme is stored permanently in the settings database and loaded automatically upon application restart.

---

## 🛠️ Compiling to a Standalone Executable & Windows Installer

### 1. Build PyInstaller EXE
You can compile the python application into a standalone Windows program folder so office staff can run it without Python installed.

1. Open `cmd` in the canonical project root directory.
2. Run:
   ```bash
   build_exe.bat
   ```
3. PyInstaller will compile only the canonical root source tree, bundle PySide6, and package assets into the `dist/` directory.
4. Locate the compiled executable folder inside:
   `dist/StudentManagementSystem/StudentManagementSystem.exe`

### 2. Build Windows Installer (Inno Setup)
To create a real installer setup file (`StudentManagementSystem_Setup.exe`) that users can install by double-clicking:

1. Ensure **Inno Setup 6** (or higher) is installed on your machine.
2. Compile the installer script located at `installer/StudentManagementSystem.iss` using Inno Setup Compiler (`ISCC.exe`):
   ```bash
   ISCC.exe installer/StudentManagementSystem.iss
   ```
3. The final installer file will be generated inside the `installer_output/` folder:
   `installer_output/StudentManagementSystem_Setup.exe`
4. Running this installer will guide you through a standard Windows wizard, creating Desktop and Start Menu shortcuts.

---

## 📁 System Directories & App Data Storage

To ensure compatibility with Windows security policies (as installed applications do not have write access inside the `Program Files` directory), the application uses two separate directories at runtime:

### 1. Application Installation Directory (Read-Only)
Contains the bundled executable and binary libraries. Located at:
- **Source run**: Project root directory
- **Installed app run**: `C:\Program Files\Student Management System`

### 2. Writable Application Data Directory
All changing user data is stored inside the user's local AppData folder to prevent administrative permission errors:
- **Source run**: Project root directory (for development convenience)
- **Installed app run**: `%LOCALAPPDATA%\StudentManagementSystem\`

The Writable folder contains:
- **`student_records.db`**: The SQLite database storing student metadata and app settings.
- **`student_photos/`**: Profile photo image files.
- **`backups/`**: Compressed system backup ZIP archives.
- **`assets/`**: Runtime-generated default avatar images.

> [!WARNING]
> **Data Backup Before Uninstalling:**
> When uninstalling the application, Windows does not automatically delete your `%LOCALAPPDATA%\StudentManagementSystem` directory. However, to prevent any accidental data loss, it is highly recommended to **Create a Full Backup** from the **Export / Backup** page and copy the generated backup ZIP file to an external drive before uninstalling or modifying the software.
