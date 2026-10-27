; 需要 Inno Setup 6 (https://jrsoftware.org/isdl.php)
#define MyAppName    "UAV 航測影像自動化處理工具"
#define MyAppVersion "1.1.0"
#define MyAppExe     "run_uav_GCP2.exe"

[Setup]
AppId={{8E3F5B1A-6C2D-4F7A-9B1E-3A5D7C9E2F41}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\UAV_Mapper
DefaultGroupName=UAV Mapper
DisableProgramGroupPage=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=Output
OutputBaseFilename=UAV_Mapper_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExe}
; 若要中文介面:下載 ChineseTraditional.isl 放進 Inno 的 Languages 資料夾,
; 再於 [Languages] 加入: Name: "zhtw"; MessagesFile: "compiler:Languages\ChineseTraditional.isl"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "installdeps"; Description: "安裝/檢查必要元件 (WSL2、Docker Desktop、ODM 影像) - 建議勾選"; GroupDescription: "必要元件:"
Name: "desktopicon"; Description: "建立桌面捷徑"; GroupDescription: "捷徑:"

[Files]
Source: "dist\run_uav_GCP2\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "setup\*"; DestDir: "{app}\setup"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Tasks: desktopicon

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\setup\install_prereq.ps1"" -AppDir ""{app}"""; StatusMsg: "正在安裝 WSL2 與 Docker Desktop (需網路,請耐心等候)..."; Flags: waituntilterminated; Tasks: installdeps
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\setup\pull_odm.ps1"""; StatusMsg: "正在下載 ODM 影像 (數 GB)..."; Flags: waituntilterminated runasoriginaluser; Tasks: installdeps; Check: not RebootFlagExists

[UninstallDelete]
Type: files; Name: "{app}\needs_reboot.flag"

[Code]
function RebootFlagExists(): Boolean;
begin
  Result := FileExists(ExpandConstant('{app}\needs_reboot.flag'));
end;

function NeedRestart(): Boolean;
begin
  Result := RebootFlagExists();
end;
