$ErrorActionPreference = 'Continue'
$Host.UI.RawUI.WindowTitle = 'UAV 航測工具 - 下載 ODM 影像'
function Say($m, $c = 'Cyan') { Write-Host "[UAV] $m" -ForegroundColor $c }

$dockerDir = Join-Path $env:ProgramFiles 'Docker\Docker'
$docker = (Get-Command docker -ErrorAction SilentlyContinue).Source
if (-not $docker) { $docker = Join-Path $dockerDir 'resources\bin\docker.exe' }

function Docker-Ready { & $docker info *> $null; return ($LASTEXITCODE -eq 0) }

if (-not (Test-Path $docker)) {
    Say '找不到 Docker,請先完成 Docker Desktop 安裝。' 'Red'; Read-Host '按 Enter 關閉'; exit 1
}

if (-not (Docker-Ready)) {
    Say '啟動 Docker Desktop ...'
    $exe = Join-Path $dockerDir 'Docker Desktop.exe'
    if (Test-Path $exe) { Start-Process $exe }
    $ok = $false
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Seconds 5
        Write-Host '.' -NoNewline
        if (Docker-Ready) { $ok = $true; break }
    }
    Write-Host ''
    if (-not $ok) {
        Say 'Docker 尚未就緒。請手動開啟 Docker Desktop;ODM 影像會在第一次執行處理時自動下載。' 'Yellow'
        Read-Host '按 Enter 關閉'; exit 2
    }
}
Say 'Docker 已就緒。' 'Green'

$image = 'opendronemap/odm:latest'
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    & nvidia-smi *> $null
    if ($LASTEXITCODE -eq 0) { $image = 'opendronemap/odm:gpu'; Say '偵測到 NVIDIA GPU,使用 GPU 版影像。' 'Green' }
}

Say "下載 $image (數 GB,視網速需數分鐘到數十分鐘,請勿關閉視窗)..."
$done = $false
for ($try = 1; $try -le 3 -and -not $done; $try++) {
    & $docker pull $image
    if ($LASTEXITCODE -eq 0) { $done = $true } else { Say "第 $try 次失敗,重試中..." 'Yellow'; Start-Sleep -Seconds 5 }
}

if ($done) {
    Say '全部完成!現在可以從桌面或開始選單開啟「UAV 航測影像自動化處理工具」。' 'Green'
} else {
    Say '下載失敗,不影響使用:第一次執行處理時 Docker 會自動再下載。' 'Yellow'
}
Read-Host '按 Enter 關閉此視窗'
