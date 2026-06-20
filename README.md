# Student Management System (SMS) - Windows Offline Edition

A professional, offline Windows desktop application developed in Python with **PySide6** and **SQLite** for maintaining, importing, and reporting student academic, training, and placement records.

---

## 🔑 Default Login Credentials

Access to the system requires administrative credentials. The application utilizes secure local password hashing (`bcrypt`) to verify credentials.

- **Username**: `admin`
- **Password**: `admin123`

> [!NOTE]
> You can update the administrator password at any time from the **Settings** screen inside the application.

---

## 🚀 Installation & Running Locally

Follow these steps to run the application directly from source code:

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed on your Windows machine.

### 2. Install Python Dependencies
Open your command prompt (`cmd`) in the `student_management_system` directory and install the necessary libraries:

```bash
pip install -r requirements.txt
```

*Required packages include: `PySide6`, `pandas`, `openpyxl`, `reportlab`, `bcrypt`, `pillow`, and `pyinstaller`.*

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

---

## 🛠️ Compiling to a Windows Executable (.exe)

You can compile the python application into a standalone Windows program so office staff can run it without Python installed.

1. Open `cmd` in the `student_management_system/` directory.
2. Double-click or run:
   ```bash
   build_exe.bat
   ```
3. PyInstaller will compile all files, bundle PySide6, and package assets into the `dist/` directory.
4. Locate the compiled executable inside:
   `dist/StudentManagementSystem/StudentManagementSystem.exe`

---

## 📁 System Directories

- **`database/`**: Contains SQLite schema scripts and database engine bindings.
- **`models/`**: Defines the object model layout for student entities.
- **`services/`**: Code for authentication, CSV/Excel parsing, PDF compiling, file caching, and backup actions.
- **`ui/`**: Complete set of Qt layout panels, forms, grids, and settings menus.
- **`student_photos/`**: Repository storing cropped/copied profile photos.
- **`backups/`**: Directory where data backup ZIPs are written.
- **`student_records.db`**: Active SQLite database file.
