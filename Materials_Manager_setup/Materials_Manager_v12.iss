; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Materials Manager"
#define MyAppVersion "1.3"
#define MyAppPublisher "KilTech Enterprise"
#define MyAppExeName "Materials_Manager.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{7D593C14-9BE7-465C-9B79-A11281FF7ABF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
; "ArchitecturesAllowed=x64compatible" specifies that Setup cannot run
; on anything but x64 and Windows 11 on Arm.
ArchitecturesAllowed=x64compatible
; "ArchitecturesInstallIn64BitMode=x64compatible" requests that the
; install be done in "64-bit mode" on x64 or Windows 11 on Arm,
; meaning it should use the native 64-bit Program Files directory and
; the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=C:\Users\Consar-Kilpatrick\PycharmProjects\materials_manager\Setup_Tutorials_and_License\License - GNUv3.txt
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=C:\Users\Consar-Kilpatrick\PycharmProjects\materials_manager\Materials_Manager_setup
OutputBaseFilename=Materials Manager v1.3
SetupIconFile=C:\Users\Consar-Kilpatrick\PycharmProjects\materials_manager\ico_file\win_setup_icon-ico.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\Consar-Kilpatrick\PycharmProjects\materials_manager\Materials_Manager\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Consar-Kilpatrick\PycharmProjects\materials_manager\Materials_Manager\_internal\*"; DestDir: "{app}/_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Consar-Kilpatrick\PycharmProjects\materials_manager\Materials_Manager\jobs.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Consar-Kilpatrick\PycharmProjects\materials_manager\Materials_Manager\materials.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Consar-Kilpatrick\PycharmProjects\materials_manager\Materials_Manager\users.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Consar-Kilpatrick\PycharmProjects\materials_manager\Materials_Manager\materialsAPI.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Consar-Kilpatrick\PycharmProjects\materials_manager\Materials_Manager\materials-data.json"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

