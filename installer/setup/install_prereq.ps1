param([Parameter(Mandatory=$true)][string]$AppDir)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$Host.UI.RawUI.WindowTitle = 'UAV 航測工具 - 安裝必要元件 (WSL2 / Docker)'

$flag = Join-Path $AppDir 'needs_reboot.flag'
Remove-Item $flag -ErrorAction SilentlyContinue
$needReboot = $false

function Say($m, $c = 'Cyan') { Write-Host "[UAV] $m" -ForegroundColor $c }
function Fail($m, $code) { Say $m 'Red'; Read-Host '按 Enter 鍵關閉此視窗'; exit $code }

# ---- 1. 系統檢查 ----
if ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64') { Fail '僅支援 64 位元 (x64) Windows。' 11 }
if ([Environment]::OSVersion.Version.Build -lt 19041) {
    Fail 'Windows 版本過舊,需 Windows 10 2004 (build 19041) 或 Windows 11 才能使用 WSL2/Docker。' 10
}
$cs  = Get-CimInstance Win32_ComputerSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
if (-not ($cs.HypervisorPresent -or $cpu.VirtualizationFirmwareEnabled)) {
    Say '警告: 偵測到 BIOS/UEFI 可能尚未啟用虛擬化 (Intel VT-x / AMD-V)。' 'Yellow'
    Say '      若重開機後 Docker 無法啟動,請進入 BIOS 開啟虛擬化功能。' 'Yellow'
}

# ---- 2. WSL2 所需 Windows 功能 ----
foreach ($f in 'Microsoft-Windows-Subsystem-Linux', 'VirtualMachinePlatform') {
    $st = (Get-WindowsOptionalFeature -Online -FeatureName $f -ErrorAction SilentlyContinue).State
    if ($st -ne 'Enabled') {
        Say "啟用 Windows 功能: $f ..."
        Enable-WindowsOptionalFeature -Online -FeatureName $f -All -NoRestart | Out-Null
        $needReboot = $true
    } else { Say "Windows 功能已啟用: $f" 'Green' }
}
if (-not $needReboot) {
    try { Say '更新 WSL ...'; & wsl.exe --update 2>&1 | Out-Host; & wsl.exe --set-default-version 2 2>&1 | Out-Host } catch {}
}

# ---- 3. Docker Desktop ----
$dockerExe = Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'
if (Test-Path $dockerExe) {
    Say 'Docker Desktop 已安裝,略過。' 'Green'
} else {
    $inst = Join-Path $AppDir 'setup\DockerDesktopInstaller.exe'   # 離線安裝檔 (可選)
    if (-not (Test-Path $inst)) {
        $inst = Join-Path $env:TEMP 'DockerDesktopInstaller.exe'
        $url  = 'https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe'
        Say '下載 Docker Desktop (約 500 MB,請稍候)...'
        try { Invoke-WebRequest -Uri $url -OutFile $inst -UseBasicParsing }
        catch { Fail "下載 Docker Desktop 失敗: $_`n請確認網路,或手動安裝 Docker Desktop 後再執行本工具。" 20 }
    }
    Say '安裝 Docker Desktop (靜默安裝,需數分鐘)...'
    $p = Start-Process -FilePath $inst -ArgumentList 'install', '--quiet', '--accept-license', '--backend=wsl-2' -Wait -PassThru
    if ($p.ExitCode -ne 0) { Fail "Docker Desktop 安裝失敗 (代碼 $($p.ExitCode))。" 21 }
    Say 'Docker Desktop 安裝完成。' 'Green'
    $needReboot = $true
}

# ---- 4. 將目前登入使用者加入 docker-users ----
$u = $cs.UserName
if ($u -and (Test-Path $dockerExe)) {
    & net.exe localgroup docker-users "$u" /add 2>$null | Out-Null
    Say "已確認使用者 $u 在 docker-users 群組。"
}

# ---- 5. 需要重開機: 登記重開後自動下載 ODM ----
if ($needReboot) {
    Set-Content -Path $flag -Value 'reboot'
    $cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$AppDir\setup\pull_odm.ps1`""
    New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce' `
        -Name 'UAV_ODM_Setup' -Value $cmd -PropertyType String -Force | Out-Null
    Say '需要重新開機。重開並登入後,系統會自動開啟視窗下載 ODM 影像。' 'Yellow'
} else {
    Say '必要元件皆已就緒。' 'Green'
}
Start-Sleep -Seconds 4
exit 0
