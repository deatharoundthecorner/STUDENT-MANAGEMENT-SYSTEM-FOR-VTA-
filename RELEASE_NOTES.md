# Student Management System — Release Notes v1.1.0

**Release Version:** v1.1.0<br>
**Build Date:** November 1, 2026<br>
**Installer File:** `StudentManagementSystem_Setup_v1.1.0.exe`<br>
**Installer File Size:** 69,220,412 bytes (~66.01 MB)<br>
**SHA-256 Checksum:** `8E666DD5CC051441C4FEC5DC600596D9C9F6820B6AC09A54C5DFEE75F6A1B13E`<br>
**Release Asset Path:** `release_candidate_v1.1.0_phase32\StudentManagementSystem_Setup_v1.1.0.exe`<br>
**Target Operating System:** Microsoft Windows 10 / Windows 11 (64-bit)<br>
**Publishing Status:** Staged Release Candidate (Ready for Production Release Authorization)

---

## 🌟 Executive Summary of v1.1.0

Student Management System v1.1.0 represents a comprehensive evolution over the initial v1.0.1 release. It introduces an enterprise-grade visual design system inspired by modern productivity interfaces (ChatGPT-inspired neutral tones), 64.4% distribution package size optimization, Argon2id cryptographic password security, in-app administrator password lifecycle management, and rigorous offline verification.

---

## 🚀 Key Improvements in v1.1.0

### 1. Professional UI Redesign & ChatGPT-Inspired Design System
- **Modern Neutral Surface Architecture:** Transitioned from harsh high-saturation colors to refined, neutral slate containers (`#F8FAFC` light canvas / `#0B1120` dark canvas) with subtle borders and card elevation.
- **Header & Navigation Modernization:** Header features a clean breadcrumb bar, prominent theme toggle pill button with animated sun/moon states, and authenticated administrator session indicator.
- **Executive Dashboard Layout:** Fully responsive grid layout organizing aggregate metrics (Total Cohort, Dropouts, Theory Passes, NVQ Level 3, NVQ Level 4, OJT Placements, Career Employment) with high-contrast, color-coded progress bars.
- **Dedicated Empty States:** Clear, guided empty states on the Dashboard, Student Records Directory, and System Backup tables that provide instructional context when no data exists.
- **Clean Action Controls:** Student directory table allocates 230px for the action column, providing individual, legible **View** (blue), **Edit** (emerald), and **Delete** (red) action buttons with clear SVG icons and hover styling.
- **Responsive Registration & Editing Forms:** Two-column grid with dedicated photo selection/preview, separate scrollable fields area, and docked footer bar preventing control overlap.

### 2. Administrator Password Lifecycle Management
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

### 3. Packaging & Distribution Optimization (64.4% Smaller)
- **Installer Package:** Reduced from **194.59 MB down to 66.01 MB** (**64.4% reduction**).
- **Installed Footprint:** Reduced from **725.91 MB down to 260.78 MB** (**64.1% reduction**).
- **Excluded Bloatware:** Removed Chromium WebEngine, QtQuick/QML, and Qt3D runtimes while maintaining complete native Qt6 desktop widget and SVG rendering capabilities.

### 4. External Friend QA Audit Passed
- An independent quality assurance review was conducted on external Windows 10/11 workstations with varying display resolutions (1080p, 1440p, 4K) and scaling factors (100%, 125%, 150%).
- All core workflows (Setup, Sign In, Registration, Table Actions, Excel/CSV Import, PDF Export, System Backup, Uninstallation) were validated and passed.

---

## 🔒 Verification & Checksum Manifest

All release assets are cryptographically verifiable:

| File Name | File Size (Bytes) | SHA-256 Digest |
| :--- | :---: | :--- |
| `StudentManagementSystem_Setup_v1.1.0.exe` | **69,220,412** | `8E666DD5CC051441C4FEC5DC600596D9C9F6820B6AC09A54C5DFEE75F6A1B13E` |
| `SHA256SUMS.txt` | **106** | `SHA-256 manifest file` |

Verify via Windows PowerShell:
```powershell
Get-FileHash .\StudentManagementSystem_Setup_v1.1.0.exe -Algorithm SHA256
```

---

## 📦 Staged GitHub Release Command (For Explicit User Authorization)

When public release authorization is granted by the repository owner, run the following command using the GitHub CLI:

```bash
gh release create v1.1.0 \
    "release_candidate_v1.1.0_phase32\StudentManagementSystem_Setup_v1.1.0.exe#Student Management System v1.1.0 Windows Setup" \
    "release_candidate_v1.1.0_phase32\SHA256SUMS.txt#SHA-256 Checksum Manifest" \
    --title "Student Management System v1.1.0 (Windows Desktop Edition)" \
    --notes-file RELEASE_NOTES.md
```
