$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DistDir = Join-Path $ProjectRoot 'dist'
$AppDir = Join-Path $DistDir 'StudentManagementSystem'
$InstallerScript = Join-Path $ProjectRoot 'installer\StudentManagementSystem.iss'
$InstallerOutput = Join-Path $ProjectRoot 'installer_output'

$MirrorPath = Join-Path $ProjectRoot 'student_management_system'
$MainPath = Join-Path $ProjectRoot 'main.py'
$SpecPath = Join-Path $ProjectRoot 'StudentManagementSystem.spec'

Write-Host "Working directory: $((Get-Location).Path)"
Write-Host "Canonical root: $ProjectRoot"
Write-Host "Mirrored duplicate: $MirrorPath"
Write-Host "Build main.py: $MainPath"
Write-Host "PyInstaller spec: $SpecPath"
Write-Host "Inno Setup script: $InstallerScript"

function Assert-NotInMirror([string[]] $PackageInputs) {
    $mirrorFullPath = [IO.Path]::GetFullPath($MirrorPath).TrimEnd('\') + '\'
    foreach ($inputPath in $PackageInputs) {
        $inputFullPath = [IO.Path]::GetFullPath($inputPath)
        if ($inputFullPath.StartsWith($mirrorFullPath, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Release package input includes the archival mirror: $inputFullPath"
        }
    }
}

Assert-NotInMirror @($MainPath, $SpecPath, $InstallerScript)

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw 'Python launcher (py) is required. Install Python 3.11+ and ensure it is on PATH.'
}

if (-not (Get-Command iscc -ErrorAction SilentlyContinue)) {
    throw 'Inno Setup compiler (iscc) is required. Install Inno Setup 6 and ensure it is on PATH.'
}

Set-Location $ProjectRoot
py -m PyInstaller --noconfirm --onedir --name StudentManagementSystem --specpath $ProjectRoot $SpecPath

if (-not (Test-Path $AppDir)) {
    throw "PyInstaller output not found at $AppDir"
}

New-Item -ItemType Directory -Force -Path $InstallerOutput | Out-Null
& iscc.exe $InstallerScript

Write-Host "Release build complete. Output folder: $InstallerOutput"
