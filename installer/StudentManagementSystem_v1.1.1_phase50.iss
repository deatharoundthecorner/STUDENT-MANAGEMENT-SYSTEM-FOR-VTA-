; Inno Setup Script - Phase 50 Release Candidate v1.1.1
; Standalone Windows installer packaging
#define MyAppName "Student Management System"
#define MyAppVersion "1.1.1"
#define MyAppPublisher "SMS Admin"
#define MyAppExeName "StudentManagementSystem.exe"

#ifndef AppSourceDir
#define AppSourceDir "..\dist_phase50\StudentManagementSystem"
#endif

#ifndef AppOutputDir
#define AppOutputDir "..\release_candidate_v1.1.1_phase50"
#endif

[Setup]
AppId={{5E2856FC-DE5C-4F93-8BEA-A8E2E5B1D89F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir={#AppOutputDir}
OutputBaseFilename=StudentManagementSystem_Setup_v1.1.1
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=65536
WizardStyle=modern
SetupIconFile=..\assets\branding\app_icon.ico
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardImageFile=wizard_large.bmp
WizardSmallImageFile=wizard_small.bmp
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog commandline
VersionInfoVersion=1.1.1.0
VersionInfoProductVersion=1.1.1.0
VersionInfoTextVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#AppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
