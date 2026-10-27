@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==== [1/3] 安裝打包所需套件 ====
py -m pip install --upgrade pip
py -m pip install pyinstaller pillow pyproj tkintermapview || goto :err

echo ==== [2/3] PyInstaller 打包成 exe ====
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
py -m PyInstaller --noconfirm --clean --windowed --name run_uav_GCP2 ^
  --collect-all pyproj --collect-all tkintermapview ^
  run_uav_GCP2EXE.py || goto :err
if not exist "dist\run_uav_GCP2\run_uav_GCP2.exe" goto :err

echo ==== [3/3] 以 Inno Setup 產生安裝檔 ====
set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
  echo 找不到 Inno Setup 6,請先安裝: https://jrsoftware.org/isdl.php
  goto :err
)
%ISCC% installer.iss || goto :err
echo.
echo 完成! 安裝檔位置: Output\UAV_Mapper_Setup.exe
pause
exit /b 0
:err
echo.
echo *** 發生錯誤,請檢查上方訊息 ***
pause
exit /b 1
