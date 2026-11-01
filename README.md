# Student Management System (SMS) — Windows Desktop Native Edition

[![Release Version](https://img.shields.io/badge/Release-v1.1.0-blue.svg)](https://github.com/deatharoundthecorner/STUDENT-MANAGEMENT-SYSTEM-FOR-VTA-/releases/tag/v1.1.0)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-PySide6%20(Qt%206)-41CD52.svg)](https://www.qt.io/qt-for-python)
[![Security](https://img.shields.io/badge/Security-Argon2id%20PHC-059669.svg)](https://tools.ietf.org/html/rfc9106)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

A high-performance, offline Windows desktop application engineered in Python with **PySide6 (Qt 6)** and **SQLite 3**. Designed specifically for vocational institutes, technical training academies, and educational administrators to track student enrollments, academic examinations, NVQ certification levels (Level 3 & Level 4), on-the-job training (OJT) industrial attachments, and graduate employment pathways.

---

## 📥 Direct Windows Installer Download

You do not need Python or developer tools to run the Student Management System. Download the official standalone Windows installer package directly from the verified GitHub release below:

| Release Package | File Name | Platform | Cryptographic Integrity |
| :--- | :--- | :---: | :--- |
| **Official v1.1.0 Release** | [**StudentManagementSystem_Setup_v1.1.0.exe**](https://github.com/deatharoundthecorner/STUDENT-MANAGEMENT-SYSTEM-FOR-VTA-/releases/download/v1.1.0/StudentManagementSystem_Setup_v1.1.0.exe) | Windows 10 / 11 (64-bit) | Verify with [SHA256SUMS.txt](https://github.com/deatharoundthecorner/STUDENT-MANAGEMENT-SYSTEM-FOR-VTA-/releases/download/v1.1.0/SHA256SUMS.txt) |

### 🛠️ Windows Installation Steps:
1. Download **`StudentManagementSystem_Setup_v1.1.0.exe`** from the release link above.
2. Double-click the downloaded executable to start the setup wizard.
3. **Microsoft Defender SmartScreen Notice:**
   - Because this is an independent software build without an enterprise code-signing certificate, Windows SmartScreen may display an alert (*"Windows protected your PC"*).
   - Click **More info**.
   - Click **Run anyway**.
4. Choose your installation location (defaults to `C:\Program Files\Student Management System`).
5. Desktop and Start Menu shortcuts will be created automatically.

### 🔍 Cryptographic Checksum Verification (PowerShell):
To verify that your downloaded installer has not been modified or corrupted, run:
```powershell
Get-FileHash .\StudentManagementSystem_Setup_v1.1.0.exe -Algorithm SHA256
```
Compare the output against the published checksum in `SHA256SUMS.txt`.

---

## ✨ Key Features & Capabilities

- **Institutional Analytics Dashboard:** Real-time metrics tracking total student intake, completion rates, NVQ Level 3 & Level 4 success rates, active OJT placements, and career employment outcomes with responsive charts and progress bars.
- **Comprehensive Student Dossiers:** Complete biographical records including national ID/NIC numbers, contact numbers, residential addresses, training records, and local profile photo storage.
- **Directory Search & Multi-Tier Filtering:** Fast pagination (50 records per page), keyword search across multiple attributes, and cohort filter dropdowns (Enrollment Year, Dropout status, Exam results, NVQ milestones, OJT placement, Employment status).
- **Batch Excel & CSV Data Ingestion:** Upload large cohorts with auto-mapping headers, real-time previewing of the top 10 rows, automated duplicate ID skipping, and detailed validation error reporting.
- **Reporting & ReportLab PDF Generation:** One-click exports to Microsoft Excel (`.xlsx`), CSV (`.csv`), formatted landscape summary PDF tables, and individual student profile dossiers with student photos.
- **Zero-Data-Loss System Backups:** In-app creation and restoration of timestamped, compressed ZIP snapshots bundling both SQLite databases and the profile photo directory.
- **Modern Theme System (Day & Night Modes):** Crisp light institutional theme and deep slate dark theme adhering to clean, restrained design principles with instant topbar theme toggle.
- **Enterprise-Grade Offline Security:** Argon2id password hashing, automatic session inactivity lock (default 15 minutes), and localized SQLite audit logging.

---

## 🧰 Technology Stack

- **Application Logic:** Python 3.9+
- **Desktop Graphical Interface:** PySide6 6.8+ (Qt 6 for Python)
- **Database Engine:** SQLite 3 (local file-based relational storage with WAL mode)
- **Password Hashing:** Argon2id via `argon2-cffi` (RFC 9106 PHC compliant)
- **Data Analysis & Export:** `pandas`, `openpyxl`
- **Document & PDF Generation:** `ReportLab`
- **Image Processing:** `Pillow` (PIL)
- **Packaging & Setup:** `PyInstaller` (optimized runtime) and `Inno Setup 6`

---

## 🔐 Administrator Authentication & Password Management

The Student Management System operates completely offline and ships **without hardcoded default passwords**.

### 1. First-Run Administrator Setup
When launching the application for the first time with a fresh database:
1. The **Administrator Setup Wizard** opens automatically.
2. Enter your desired administrator username (minimum 3 characters).
3. Enter a master password satisfying the institutional password policy.
4. Confirm your password and click **Create Administrator Account**.
5. The setup wizard transitions directly to the Sign-In screen.

### 2. How to Change the Administrator Password
Authenticated administrators can update their master credentials at any time:
1. Sign in to the application as an administrator.
2. In the left navigation sidebar, click **Settings**.
3. Locate the **Account & Security — Administrator Password** section.
4. Verify that the session indicator shows `Active Account: <your-username> (Administrator)`.
5. Enter your **Current Password**.
6. Enter your **New Password** and observe the live, color-coded password strength meter.
7. Re-type the new password into **Confirm New Password**.
8. Click **Update Administrator Password**.
9. A confirmation alert verifies the update. Log out from the sidebar and sign back in using your new credentials.

### 3. Password Complexity Policy
All administrator passwords (both initial setup and subsequent changes) must satisfy these strict security rules:
- **Minimum Length:** Must be at least 8 characters long.
- **Character Diversity:** Passwords under 15 characters must contain both letters and non-letter characters (numbers or symbols).
- **Long Passphrases (Recommended):** Passphrases 15 characters or longer are considered high-entropy passphrases and do not require symbol mixing.
- **No Surrounding Whitespace:** Passwords cannot start or end with spaces.
- **Common Password Rejection:** Trivial or guessable passwords (e.g. `password123`, `admin123`, `12345678`) are automatically blocked.
- **Cryptographic Storage:** Credentials are saved using Argon2id (`memory_cost=19456`, `time_cost=2`, `parallelism=1`) with unique per-user salts. Plaintext passwords are never stored, logged, or exposed in audit trails.
- **Upgrade and Reinstallation Preservation:** Existing administrator credentials and student records are preserved across application reinstalls or updates because writable data is decoupled from the installation directory.

---

## 📂 System Directories & Data Architecture

To ensure full compliance with standard Windows user permission boundaries (standard users cannot write to `C:\Program Files`) and to protect production records during development, the application strictly separates executable code from user data:

### 1. Installation Directory (Read-Only)
Contains the compiled binaries, dynamic Qt libraries, and static graphics:
- **Default Location:** `C:\Program Files\Student Management System\`

### 2. Writable Application Data Directory
All persistent data (student records, photos, backups, and security audit logs) resides strictly outside the project repository in the current user's local AppData folder:
- **Installed Application (Production):** `%LOCALAPPDATA%\StudentManagementSystem\`
- **Source / Development Mode:** `%LOCALAPPDATA%\StudentManagementSystem-Dev\`
- **Automated QA & Custom Environment:** Configurable via the `SMS_DATA_DIR` environment variable (highest priority).

| Folder / File | Purpose |
| :--- | :--- |
| `student_records.db` | Primary SQLite database storing student records, user accounts, application settings, and audit logs. |
| `student_photos/` | High-resolution student photo images saved as local files. |
| `backups/` | Compressed timestamped ZIP archives containing complete database and photo snapshots. |
| `logs/` | Local security audit (`security.log`) and system operational logs. |
| `assets/` | Runtime asset cache including default student avatars. |

> [!IMPORTANT]
> **Data Privacy & Local Storage Guarantee:**
> All student personal data, identification numbers, and contact details are stored **strictly on the local computer** inside the user data directory. The software never transmits or synchronizes institutional records to external cloud endpoints, third-party services, or analytics providers.

> [!TIP]
> **Database Backup Recommendation:**
> Before reinstalling Windows or moving to a new computer, navigate to the **Export / Backup** page in the application, click **Create Full Backup**, and copy the resulting ZIP file to a secure external USB drive or network share.

---

## 💻 Running from Source Code (Developer Mode)

If you prefer to run or build the application from source code:

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/deatharoundthecorner/STUDENT-MANAGEMENT-SYSTEM-FOR-VTA-.git
cd student_management_system
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python -m unittest discover tests
```

### 4. Launch Application
```bash
python main.py
```
*Note: In development mode, all writable databases, photos, backups, and logs are automatically isolated in `%LOCALAPPDATA%\StudentManagementSystem-Dev\` to ensure your local production records are never modified.*

---

## ⚠️ Known Limitations & Support

- **Completely Offline by Design:** The system operates in a private, offline workstation environment. It does not synchronize with cloud providers or send telemetry.
- **No Remote Email Recovery:** Because no external cloud email or SMS gateways are integrated, administrators must keep their master password safe. In the event of lost credentials, restore a previous database backup.
- **Single-Workstation Architecture:** Designed for single-operator administrative terminals; concurrent multi-user network sharing of a single raw SQLite file across network shares is not recommended.
- **Windows SmartScreen Alert:** As an independent open-source release without an expensive commercial EV certificate, Windows may show a SmartScreen warning. Follow the installation instructions above to bypass it safely.
- **Bug Reports & Support:** If you encounter unexpected behavior or wish to request features, please open an issue on the [GitHub Issues](https://github.com/deatharoundthecorner/STUDENT-MANAGEMENT-SYSTEM-FOR-VTA-/issues) tracker.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
