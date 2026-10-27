# UAV 航測工具 安裝檔製作說明

## 開發者(只做一次)
1. 在 **Windows** 電腦安裝 Python 3.10~3.12(勾選 py launcher)與 [Inno Setup 6](https://jrsoftware.org/isdl.php)
2. 雙擊 `build_all.bat`
3. 成功後取得 `Output\UAV_Mapper_Setup.exe`,即可發給使用者

(可選)把 `DockerDesktopInstaller.exe` 放進 `setup\` 再打包,即可離線安裝 Docker。

## 使用者
1. 對 `UAV_Mapper_Setup.exe` 按右鍵 → 以系統管理員身分執行
2. 保持勾選「安裝/檢查必要元件」
3. 若出現重開機提示請重開;登入後會自動跳出視窗下載 ODM 影像(數 GB)
4. 完成後從桌面捷徑開啟程式

## 成果檔案
- `odm_orthophoto/odm_orthophoto.tif` 正射影像
- `odm_dem/dsm.tif` 數值地表模型 (含建物、植被)
- `odm_dem/dtm.tif` 裸露地形 DEM (勾選 DTM 且為高精度/超大範圍模式時才會產出)

## 注意事項
- Docker Desktop 對大型企業(>250 人或年營收 >1,000 萬美元)需付費授權
- 主程式每次執行時,容器內會 `pip install numpy<2`,處理時需連網
- 需 Windows 10 2004+/11 64 位元,BIOS 須開啟虛擬化;建議 16GB RAM 以上
- 未簽章的 PyInstaller exe 偶爾被防毒誤報
- 解除安裝不會移除 Docker Desktop 與 ODM 影像
