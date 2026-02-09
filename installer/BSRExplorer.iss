; Inno Setup script for BSRExplorer Windows Installer
; Version is passed via /DMyAppVersion=x.y.z at compile time

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

[Setup]
AppId={{B5A2E3F1-9C4D-4E6A-8F7B-1D2E3F4A5B6C}
AppName=BSRExplorer
AppVersion={#MyAppVersion}
AppPublisher=ashajkofci
AppPublisherURL=https://github.com/ashajkofci/BSRExplorer
DefaultDirName={autopf}\BSRExplorer
DefaultGroupName=BSRExplorer
OutputBaseFilename=BSRExplorer-Windows-Installer
OutputDir=..\
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName=BSRExplorer

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\BSRExplorer.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\BSRExplorer"; Filename: "{app}\BSRExplorer.exe"
Name: "{group}\{cm:UninstallProgram,BSRExplorer}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\BSRExplorer"; Filename: "{app}\BSRExplorer.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\BSRExplorer.exe"; Description: "{cm:LaunchProgram,BSRExplorer}"; Flags: nowait postinstall skipifsilent
