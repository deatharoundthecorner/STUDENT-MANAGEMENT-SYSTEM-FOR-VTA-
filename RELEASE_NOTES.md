# Student Management System — Release Notes

## 🛠️ Release Notes v1.1.1 (Maintenance & Quality Release)

**Release Version:** v1.1.1 (Maintenance Candidate)<br>
**Target Platform:** Microsoft Windows 10 / Windows 11 (64-bit)<br>
**Release Type:** Maintenance, Usability & Storage Security Update<br>
**Database Compatibility:** 100% backward compatible with v1.1.0 and v1.0.1 databases

---

### 🌟 Summary of v1.1.1 Improvements

Student Management System v1.1.1 introduces user-facing workflow refinements in the Student Registration & Dossier Form, implements workstation storage boundary isolation between development and production environments, aligns security audit logging with dynamic runtime contexts, documents first-install security protocols, and incorporates comprehensive automated regression tests.

---

### 🚀 Key Improvements in v1.1.1

#### 1. Interactive ADD / EDIT Mode Workflow in Student Registration Form
- **Interactive ADD MODE Button:** Converted the top-right status badge from a passive label into a fully interactive button (`QPushButton#btnAddMode`). In EDIT mode, the button transitions to **`+ Switch to Add Mode`**, enabling administrators to immediately register a new student without leaving the form.
- **Dedicated Mode Indicators:** Added a distinct, visible `EDIT MODE` indicator pill (`QLabel#lblModeIndicator`) when viewing or editing existing student records, clearly distinguishing Edit mode from Add mode.
- **Unsaved Changes Protection:** Added `has_unsaved_changes()` detection. When switching modes or resetting the form with uncommitted changes, a modal confirmation dialog prompts the user (*"You have unsaved information in the form. Discard and switch to Add Mode?"*). Selecting **No** keeps all unsaved inputs intact; selecting **Yes** safely resets the form.
- **Clean Field & State Reset:** Transitioning from Edit to Add mode cleanly purges all previously loaded student data, phone numbers, addresses, and selected photographs, resetting the form for a new registration.

#### 2. Local Storage Architecture & Data Isolation
- **Development Environment Isolation:** When running the application from source code (`python main.py`), all runtime databases, photos, backups, and logs are now strictly isolated to `%LOCALAPPDATA%\StudentManagementSystem-Dev\`. This prevents development testing from corrupting or modifying local production institutional records.
- **Installed Runtime Integrity:** Compiled Windows desktop installations continue using `%LOCALAPPDATA%\StudentManagementSystem\`.
- **Dynamic Security Logging:** Updated `get_security_logger()` to resolve `writable_dir / logs / security.log` dynamically based on the active runtime environment, while preserving automatic secret redaction (`password=[REDACTED]`).
- **QA Testing Override:** The `SMS_DATA_DIR` environment variable retains top priority across all runtime modes for isolated test execution.

#### 3. First-Run Administrator Setup & Privacy Guarantees
- **No Shared Default Passwords:** Explicitly documented that no default administrator credentials exist. Fresh installations mandate custom account creation via the First-Run Setup Wizard.
- **Argon2id Memory-Hard Cryptography:** Confirmed unique per-user cryptographic salts and RFC 9106 PHC Argon2id formatting for all user accounts, with zero plaintext persistence in databases or logs.
- **Offline Data Sovereignty:** Explicitly documented that all student dossiers, identification numbers, contact information, photos, and backups remain 100% contained within the local workstation and are never transmitted to external cloud services or telemetry endpoints.
- **Preservation on Reinstallation:** Reaffirmed that application reinstalls or updates leave the `%LOCALAPPDATA%` data directory intact.

#### 4. Automated Regression Test Suite
- Added permanent automated regression tests (`tests/test_v111_regression.py`) covering storage isolation, logging redaction, first-run wizard detection, password security, ADD/EDIT mode transitions, unsaved change prompts, duplicate ID rejection, and record immutability.
- All 42 unit and regression tests pass with 0 failures and 0 errors.

---

## 📦 Release Notes v1.1.0 (Official Public Release)

**Release Version:** v1.1.0<br>
**Build Date:** November 1, 2026<br>
**Installer File:** `StudentManagementSystem_Setup_v1.1.0.exe`<br>
**Installer File Size:** 69,220,412 bytes (~66.01 MB)<br>
**SHA-256 Checksum:** `8E666DD5CC051441C4FEC5DC600596D9C9F6820B6AC09A54C5DFEE75F6A1B13E`<br>
**Release Asset Path:** `release_candidate_v1.1.0_phase32\StudentManagementSystem_Setup_v1.1.0.exe`<br>
**Target Operating System:** Microsoft Windows 10 / Windows 11 (64-bit)<br>
**Publishing Status:** Published to GitHub Releases (Official Public Release)

---

### 🌟 Executive Summary of v1.1.0

Student Management System v1.1.0 represents a comprehensive evolution over the initial v1.0.1 release. It introduces an enterprise-grade visual design system inspired by modern productivity interfaces (ChatGPT-inspired neutral tones), 64.4% distribution package size optimization, Argon2id cryptographic password security, in-app administrator password lifecycle management, and rigorous offline verification.

---

### 🚀 Key Improvements in v1.1.0

#### 1. Professional UI Redesign & ChatGPT-Inspired Design System
- **Modern Neutral Surface Architecture:** Transitioned from harsh high-saturation colors to refined, neutral slate containers (`#F8FAFC` light canvas / `#0B1120` dark canvas) with subtle borders and card elevation.
- **Header & Navigation Modernization:** Header features a clean breadcrumb bar, prominent theme toggle pill button with animated sun/moon states, and authenticated administrator session indicator.
- **Executive Dashboard Layout:** Fully responsive grid layout organizing aggregate metrics (Total Cohort, Dropouts, Theory Passes, NVQ Level 3, NVQ Level 4, OJT Placements, Career Employment) with high-contrast, color-coded progress bars.
- **Dedicated Empty States:** Clear, guided empty states on the Dashboard, Student Records Directory, and System Backup tables that provide instructional context when no data exists.
- **Clean Action Controls:** Student directory table allocates 230px for the action column, providing individual, legible **View** (blue), **Edit** (emerald), and **Delete** (red) action buttons with clear SVG icons and hover styling.
- **Responsive Registration & Editing Forms:** Two-column grid with dedicated photo selection/preview, separate scrollable fields area, and docked footer bar preventing control overlap.

#### 2. Administrator Password Lifecycle Management
- **In-App Password Management:** Authenticated administrators can easily update their password from **Settings -> Account & Security**.
- **Real-Time Password Strength Meter:** Dynamic visual progress bar and text feedback guiding users to create compliant passwords, with live warnings for boundary whitespace or trivial patterns.
- **Argon2id Memory-Hard Cryptography:** All passwords use RFC 9106 Argon2id hashing with per-user cryptographic salts. Legacy bcrypt passwords from v1.0.1 are automatically and transparently upgraded to Argon2id upon login.
- **Strict Policy Enforcement:**
  - Minimum 8 characters.
  - Must include letters and non-letters (numbers or symbols) for passwords under 15 characters.
  - Passphrases of 15+ characters do not require numbers or symbols.
  - No leading or trailing spaces.
  - Rejection of common dictionary words (e.g., `password123`, `admin123`).
  - Rejection of password reuse (new password cannot equal current password).
  - Rejection of mismatched confirmation.
  - Verification of current password before committing changes.
- **Privacy & Audit Safety:** Zero plaintext passwords stored or logged in database or audit logs.

#### 3. Packaging & Distribution Optimization (64.4% Smaller)
- **Installer Package:** Reduced from **194.59 MB down to 66.01 MB** (**64.4% reduction**).
- **Installed Footprint:** Reduced from **725.91 MB down to 260.78 MB** (**64.1% reduction**).
- **Excluded Bloatware:** Removed Chromium WebEngine, QtQuick/QML, and Qt3D runtimes while maintaining complete native Qt6 desktop widget and SVG rendering capabilities.

#### 4. External Friend QA Audit Passed
- An independent quality assurance review was conducted on external Windows 10/11 workstations with varying display resolutions (1080p, 1440p, 4K) and scaling factors (100%, 125%, 150%).
- All core workflows (Setup, Sign In, Registration, Table Actions, Excel/CSV Import, PDF Export, System Backup, Uninstallation) were validated and passed.

---

### 🔒 Verification & Checksum Manifest

All release assets are cryptographically verifiable:

| File Name | File Size (Bytes) | SHA-256 Digest |
| :--- | :---: | :--- |
| `StudentManagementSystem_Setup_v1.1.0.exe` | **69,220,412** | `8E666DD5CC051441C4FEC5DC600596D9C9F6820B6AC09A54C5DFEE75F6A1B13E` |
| `SHA256SUMS.txt` | **106** | `SHA-256 manifest file` |

Verify via Windows PowerShell:
```powershell
Get-FileHash .\StudentManagementSystem_Setup_v1.1.0.exe -Algorithm SHA256
```
