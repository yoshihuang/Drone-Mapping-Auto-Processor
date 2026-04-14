import sys
import subprocess
import queue
import base64

# ==========================================
# 🛡️ 核心新功能：自動偵測與安裝必備套件 (新增 pyproj 支援座標轉換)
# ==========================================
def check_and_install_packages():
    missing_packages = []
    try: import tkintermapview
    except ImportError: missing_packages.append("tkintermapview")
    try: import PIL
    except ImportError: missing_packages.append("Pillow")
    try: import pyproj
    except ImportError: missing_packages.append("pyproj")
        
    if missing_packages:
        print("="*60)
        print(f"📦 系統偵測到缺少必要套件：{', '.join(missing_packages)}")
        print("⏳ 正在背景為您自動下載與安裝，這可能需要幾十秒鐘，請稍候...")
        print("="*60)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
            print("\n✅ 套件自動安裝成功！系統準備啟動...\n")
        except Exception as e:
            print(f"\n❌ 自動安裝失敗，請確認您的網路連線。")
            print(f"錯誤代碼：{e}")
            input("請按 Enter 鍵結束程式...")
            sys.exit(1)

check_and_install_packages()

# ==========================================
# ⬇️ 檢查通過後，載入所有模組
# ==========================================
import os
import threading
import time
import datetime
import shutil
import locale
import ctypes
import re
import pyproj
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk 
import tkintermapview
from PIL import Image, ImageDraw, ImageTk 
from PIL.ExifTags import TAGS, GPSTAGS

# 🌟 全面雙語化字典
LANG = {
    "en": {
        "title": "🚁 Drone Mapping Auto-Processor (Pro Ultimate GIS Edition)",
        "step1_title": " 📂 Step 1: Set Folders & Data ",
        "src_lbl": "Source Photos:",
        "out_lbl": "Output Folder:",
        "btn_browse": "Browse...",
        "gcp_chk": "Enable GCP (Ground Control Points)",
        "gcp_lbl": "GCP File (txt):",
        "btn_gcp_help": "📝 Format Guide",
        "btn_gcp_tutorial": "💡 How to Generate GCP",
        "step2_title": " ⚙️ Step 2: Choose Mode ",
        "mode_fast": "⚡Fast Orthophoto - Skips 3D point cloud, extremely fast",
        "mode_high": "🏗 High Precision - Detailed DSM & 3D model (< 300 imgs)",
        "mode_huge": "🗺 Huge Dataset - Split processing, prevents OOM (> 500 imgs)",
        "btn_start": "🚀 Start Auto Processing",
        "btn_init": "⚙️ System initializing...",
        "time_elapsed": "⏳ Elapsed: ",
        "log_lbl": "📜 Execution Log:",
        "map_lbl": "🗺️ UAV Flight Path & Status Map",
        "map_osm": "OpenStreetMap (Standard)",
        "map_g_sat": "Google Maps (Satellite)",
        "map_g_nor": "Google Maps (Roadmap)",
        "map_btn_fit": "🔍 Fit to All",
        "msg_err_folder": "Please set both Source and Output folders!",
        "msg_err_gcp": "Please select a valid GCP file, or uncheck the GCP option.",
        "log_wsl_fix": "🔧 Auto-configuring Windows WSL2 memory limits...\n",
        "log_wsl_done": "✅ WSL2 memory limits optimized! Restarting Docker engine...\n",
        "log_start_chk": "🐳 Checking Docker engine status...\n",
        "log_docker_sleep": "💤 Docker is sleeping, attempting to wake up...\n",
        "log_docker_wait": "⏳ Waiting for Docker to warm up (approx. 1-2 mins)\n",
        "log_docker_ready": "✅ Docker engine is ready! Taking over the task.\n\n",
        "log_docker_fail": "❌ Timeout! Please open Docker Desktop manually.\n",
        "log_docker_err": "❌ Failed to auto-start Docker.\n",
        "log_gpu_chk": "🔍 Detecting GPU hardware...\n",
        "log_gpu_yes": "🌟 NVIDIA GPU detected, switching to CUDA dedicated engine!\n",
        "log_gcp_yes": "📍 GCP File detected, enabling high-precision georeferencing!\n",
        "log_odm_start": "\n--- 🏁 Calling ODM Engine, processing started ---\n\n",
        "log_clean_start": "🧹 Cleaning up temporary files...\n",
        "log_clean_done": "✨ Cleanup complete! Only orthophoto and DSM are kept.\n",
        "log_done": "✅ Processing completed successfully!\n",
        "msg_done_title": "Completed",
        "msg_done_body": "Processing and cleanup successful!\nTime: {time}\nSaved at:\n{path}",
        "msg_err_title": "Error",
        "msg_err_body": "Processing failed (Code: {code})\nPlease check the log.",
        "gcp_tut_title": "How to Generate GCP Files?",
        "gcp_tut_text": "【 How to Generate GCP Files using Professional Software? 】\n\nIt is highly recommended to use professional software to mark and export GCPs for better precision and fewer errors! Here are two common methods:\n\n⚠️ CRITICAL REQUIREMENT:\nIn photogrammetry, a single Ground Control Point MUST be identified and marked in at least 3 to 5 DIFFERENT photos to allow for 3D triangulation. Marking a point in only one photo will cause the mathematical model to fail and shrink the map!\n\n📍 Method 1: WebODM UI (Recommended)\n1. Open the WebODM web interface.\n2. Create a new project and upload your drone photos.\n3. Click 'Ground Control Points' on the project dashboard.\n4. Click on the target features directly on the photos and enter the corresponding real-world coordinates (X, Y, Z) and EPSG code on the right.\n5. Ensure each control point is marked on at least 3-5 different photos.\n6. Once all markings are complete, click 'Export' and choose `gcp_list.txt`.\n7. Load this file directly into our program!\n\n📍 Method 2: Google Earth Pro + Image Viewer (Manual/Fallback)\n1. Find obvious, immovable features in your photos (e.g., crosswalk corners, manholes).\n2. Use an image viewer (e.g., MS Paint), hover over the feature, and note the 'Pixel X, Pixel Y'.\n3. Open Google Earth Pro, find the exact same spot, hover over it, and read the 'Longitude, Latitude' and 'Elevation' at the bottom right.\n4. Download the 'GCP Format Template' from this program and fill in your data sequentially:\n   (ProjX  ProjY  Elevation  PixelX  PixelY  ImageName  GCPName)\n5. Make sure the same GCP Name appears across 3-5 different ImageNames.\n6. Save the file and load it into this program.",
        "btn_close": "Close",
        "gcp_help_title": "GCP Format Guide & Template",
        "gcp_help_text": "【 WebODM GCP File Format Guide 】\n\nPlease prepare a plain text file (.txt or .csv) matching the following format:\n\nLine 1: Enter the EPSG projection code (e.g., WGS84 use WGS84 EPSG:4326, TWD97 use EPSG:3826)\nLine 2 onwards: Enter one control point per line, separated by 'Space' or 'Tab'\n\nColumn Order:\nProj-X  Proj-Y  Elevation(Z)  Pixel-X  Pixel-Y  Image-Name  GCP-Name(Optional)\n\n【 Example (Using EPSG:3826) 】\nEPSG:3826\n208338.079 2610073.274 365.692 2971 412 MAX_0488.JPG no1\n208338.079 2610073.274 365.692 5388 2032 MAX_0490.JPG no1\n208338.079 2610073.274 365.692 3590 1787 MAX_0499.JPG no1\n...",
        "btn_gcp_dl": "📥 Download Template (gcp_template.txt)",
        "gcp_dl_title": "Save GCP Template",
        "msg_success_title": "Success",
        "msg_gcp_dl_success": "Template saved to:\n{filepath}",
        "msg_gcp_dl_err": "Save failed: {e}",
        "log_gcp_transform": "🔄 Detected non-WGS84 projection ({epsg}), auto-transforming coordinates for map display...\n",
        "log_gcp_transform_err": "⚠️ Coordinate transformation failed, cannot display markers on map (Error: {e}).\n",
        "log_gcp_loaded": "✅ Successfully pinned {count} GCPs on the map.\n",
        "log_gcp_parse_err": "⚠️ Error parsing GCP file: {e}\n",
        "log_scan_gps": "🗺️ Scanning photo GPS coordinates...\n",
        "log_photo_loaded": "✅ Successfully pinned {count} photos on the map.\n",
        "log_no_gps": "⚠️ No photos with GPS coordinates found.\n",
        "log_gcp_copy_err": "⚠️ Failed to copy GCP file: {e} (Continuing without GCP)\n",
        "log_exception": "\n❌ Exception: {e}\n"
    },
    "zh": {
        "title": "🚁 航測影像自動化處理工具 (Pro 專業定位版)",
        "step1_title": " 📂 第一步：設定資料夾與測量資料 ",
        "src_lbl": "原始照片：",
        "out_lbl": "輸出結果：",
        "btn_browse": "瀏覽...",
        "gcp_chk": "啟用 GCP (地面控制點) 提升精度",
        "gcp_lbl": "GCP 檔案 (txt)：",
        "btn_gcp_help": "📝 格式範例",
        "btn_gcp_tutorial": "💡 製作教學",
        "step2_title": " ⚙️ 第二步：選擇處理模式 ",
        "mode_fast": "⚡ 快速地圖模式 (Fast Orthophoto) - 略過點雲，速度極快",
        "mode_high": "🏗 高精度重建模式 (High Precision) - 產出細緻 3D (<300張)",
        "mode_huge": "🗺 超大範圍切割模式 (Huge Dataset) - 產出細緻 3D (>300張)",
        "btn_start": "🚀 開始全自動處理",
        "btn_init": "⚙️ 系統初始化中...",
        "time_elapsed": "⏳ 經過時間：",
        "log_lbl": "📜 執行監控 (Log)：",
        "map_lbl": "🗺️ 航線位置與即時進度圖",
        "map_osm": "開源地圖 (OpenStreetMap)",
        "map_g_sat": "Google 衛星地圖",
        "map_g_nor": "Google 標準地圖",
        "map_btn_fit": "🔍 顯示所有範圍",
        "msg_err_folder": "請先設定「原始照片」與「輸出結果」的資料夾！",
        "msg_err_gcp": "您已勾選啟用 GCP，請選擇有效的 GCP 檔案 (txt)，或取消勾選。",
        "log_wsl_fix": "🔧 正在自動解除 Windows WSL2 記憶體封印...\n",
        "log_wsl_done": "✅ 記憶體封印解除成功！強制重啟底層引擎...\n",
        "log_start_chk": "🐳 正在檢查 Docker 引擎狀態...\n",
        "log_docker_sleep": "💤 Docker 正在沉睡，嘗試發送喚醒指令...\n",
        "log_docker_wait": "⏳ 正在等待 Docker 暖機 (通常需要 1 到 2 分鐘，請喝口茶)\n",
        "log_docker_ready": "✅ Docker 引擎暖機完畢！接管任務。\n\n",
        "log_docker_fail": "❌ 等待逾時！請手動從開始選單開啟 Docker Desktop。\n",
        "log_docker_err": "❌ 無法自動啟動 Docker，請手動開啟。\n",
        "log_gpu_chk": "🔍 正在偵測 GPU 硬體環境...\n",
        "log_gpu_yes": "🌟 偵測到 NVIDIA GPU，切換至 CUDA 專用版引擎！\n",
        "log_gcp_yes": "📍 已載入 GCP 檔案，啟動高精度測量級定位系統！\n",
        "log_odm_start": "\n--- 🏁 呼叫 ODM Engine，開始運算 ---\n\n",
        "log_clean_start": "🧹 開始清理不必要的暫存檔案...\n",
        "log_clean_done": "✨ 清理完成！已刪除暫存檔，僅保留最終成果。\n",
        "log_done": "✅ 處理成功完成！請至「輸出資料夾」查看結果。\n",
        "msg_done_title": "完成",
        "msg_done_body": "運算與清理皆已成功完成！\n耗時：{time}\n檔案已存於：\n{path}",
        "msg_err_title": "錯誤",
        "msg_err_body": "運算失敗 (代碼: {code})\n請查看 Log 了解詳細原因。",
        "gcp_tut_title": "如何產生 GCP 檔案？",
        "gcp_tut_text": "【 如何使用專業軟體輔助產生 GCP 檔案？ 】\n\n強烈建議使用專業軟體來標記與匯出 GCP，比起手動輸入更精準且不易出錯！以下提供兩種常見的作法：\n\n⚠️ 極度重要提醒：\n在航測幾何原理中，同一個「真實世界控制點」必須「至少出現在 3 到 5 張不同的照片中」，演算法才能進行空間交會測量 (Triangulation)。如果每個點只在一張照片上標記，會導致數學矩陣直接崩潰縮水！\n\n📍 做法一：使用 WebODM 內建介面 (最推薦)\n1. 開啟 WebODM 網頁介面。\n2. 建立一個新專案，並上傳您的無人機照片。\n3. 在專案儀表板點選「Ground Control Points (地面控制點)」。\n4. 系統會顯示您的照片，您可以直接在照片上點擊目標特徵，並在右側輸入該點對應的真實世界座標 (X, Y, Z) 與 EPSG 代碼。\n5. 請確保同一個控制點標記在 3-5 張不同的照片上。\n6. 完成所有標記後，點擊「Export (匯出)」按鈕，選擇匯出為 `gcp_list.txt`。\n7. 將此檔案直接載入本程式即可！\n\n📍 做法二：使用 Google Earth Pro + 小畫家 (手動應急作法)\n1. 在您的無人機照片中，找尋明顯且不會移動的特徵 (例如：斑馬線交角、人孔蓋)。\n2. 使用電腦內建的看圖軟體 (如小畫家)，將滑鼠游標移到該特徵上，記下「像素座標 (Pixel X, Pixel Y)」。\n3. 打開 Google Earth Pro，找到一模一樣的地點，將游標放上去，讀取右下角的「經緯度 (Longitude, Latitude)」與「海拔高度」。\n4. 下載本程式提供的「GCP 格式範本」，將您查到的資料依序填入：\n   (投影X  投影Y  高度  像素X  像素Y  照片檔名  控制點名稱)\n5. 請務必確保同一個「控制點名稱」對應到 3-5 張不同的「照片檔名」。\n6. 存檔後載入本程式。",
        "btn_close": "關閉",
        "gcp_help_title": "GCP 格式說明與範本",
        "gcp_help_text": "【 WebODM GCP 檔案格式說明 】\n\n請準備一個純文字檔 (.txt 或 .csv)，內容必須符合以下格式：\n\n第一行：請填寫 EPSG 投影座標代碼 (例如 WGS84 填 WGS84 EPSG:4326，台灣 TWD97 填 EPSG:3826)\n第二行開始：每行輸入一個控制點，資料以「空白」或「Tab」分隔\n\n排列順序：\n投影X座標  投影Y座標  海拔高度(Z)  像素X座標  像素Y座標  照片檔名  控制點名稱(可選)\n\n【 格式範例 (以 EPSG:3826 為例) 】\nEPSG:3826\n208338.079 2610073.274 365.692 2971 412 MAX_0488.JPG no1\n208338.079 2610073.274 365.692 5388 2032 MAX_0490.JPG no1\n208338.079 2610073.274 365.692 3590 1787 MAX_0499.JPG no1\n...",
        "btn_gcp_dl": "📥 下載範本 (gcp_template.txt)",
        "gcp_dl_title": "儲存 GCP 範本檔案",
        "msg_success_title": "成功",
        "msg_gcp_dl_success": "範本已儲存至:\n{filepath}",
        "msg_gcp_dl_err": "儲存失敗: {e}",
        "log_gcp_transform": "🔄 偵測到非 WGS84 座標 ({epsg})，正在自動轉換為經緯度以顯示於地圖...\n",
        "log_gcp_transform_err": "⚠️ 座標轉換失敗，無法顯示地圖標記 (錯誤: {e})。\n",
        "log_gcp_loaded": "✅ 成功標定 {count} 個 GCP 於地圖。\n",
        "log_gcp_parse_err": "⚠️ 解析 GCP 檔案發生錯誤: {e}\n",
        "log_scan_gps": "🗺️ 正在掃描照片 GPS 座標...\n",
        "log_photo_loaded": "✅ 成功標定 {count} 張照片於地圖。\n",
        "log_no_gps": "⚠️ 未找到具備 GPS 座標的照片。\n",
        "log_gcp_copy_err": "⚠️ 無法複製 GCP 檔案：{e} (將以無 GCP 模式繼續)\n",
        "log_exception": "\n❌ Exception: {e}\n"
    }
}

class DroneProcessingApp:
    def __init__(self, root):
        self.root = root
        self.lang_code = "en"
        try:
            if os.name == 'nt':
                lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
                if lang_id in [1028, 2052, 3076, 4100, 5124]: self.lang_code = "zh"
            else:
                sys_lang = str(locale.getlocale()[0]).lower()
                if "zh" in sys_lang or "chinese" in sys_lang or "tw" in sys_lang: self.lang_code = "zh"
        except Exception: pass

        self.t = LANG[self.lang_code]
        self.root.title(self.t["title"])
        self.root.geometry("1200x800")
        self.root.configure(padx=15, pady=15)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.font_title = ("微軟正黑體", 12, "bold") if self.lang_code == "zh" else ("Segoe UI", 11, "bold")
        self.font_normal = ("微軟正黑體", 10) if self.lang_code == "zh" else ("Segoe UI", 10)
        self.font_tiny = ("Arial", 8, "bold") 
        
        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.mode_var = tk.StringVar(value="fast") 
        
        self.use_gcp = tk.BooleanVar(value=False)
        self.gcp_path = tk.StringVar()
        
        self.start_time = None
        self.is_running = False
        self.photo_markers = {}
        self.gcp_markers = {}
        self.process_handle = None
        
        self.log_queue = queue.Queue()
        self.marker_queue = queue.Queue()
        self.marker_text_visible = True
        
        self.icon_green = self.create_circle_icon("#2ECC71", "#1E8449", 10)
        self.icon_red = self.create_circle_icon("#E74C3C", "#922B21", 10)
        self.icon_triangle = self.create_triangle_icon("#000000", "#FFFFFF", 12)
        
        self.create_widgets()
        self.toggle_gcp_state() 
        
        self.root.after(100, self.process_ui_updates)
        self.root.after(200, self.check_map_zoom)

    def on_closing(self):
        self.is_running = False
        if self.process_handle:
            try: self.process_handle.terminate()
            except Exception: pass
        self.root.destroy()
        sys.exit(0)

    def create_circle_icon(self, fill_color, outline_color, size):
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, size-1, size-1), fill=fill_color, outline=outline_color)
        return ImageTk.PhotoImage(img)

    def create_triangle_icon(self, fill_color, outline_color, size):
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        points = [(size/2, 0), (0, size), (size, size)]
        draw.polygon(points, fill=fill_color, outline=outline_color)
        return ImageTk.PhotoImage(img)

    def create_widgets(self):
        left_frame = tk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_frame = tk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        frame_1 = tk.LabelFrame(left_frame, text=self.t["step1_title"], font=self.font_title, fg="#2E86C1", padx=10, pady=10)
        frame_1.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame_1, text=self.t["src_lbl"], font=self.font_normal).grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(frame_1, textvariable=self.source_path, font=self.font_normal, state='readonly', width=38).grid(row=0, column=1, padx=5)
        tk.Button(frame_1, text=self.t["btn_browse"], font=self.font_normal, command=self.browse_source).grid(row=0, column=2)
        
        tk.Label(frame_1, text=self.t["out_lbl"], font=self.font_normal).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(frame_1, textvariable=self.output_path, font=self.font_normal, state='readonly', width=38).grid(row=1, column=1, padx=5)
        tk.Button(frame_1, text=self.t["btn_browse"], font=self.font_normal, command=self.browse_output).grid(row=1, column=2)

        ttk.Separator(frame_1, orient='horizontal').grid(row=2, column=0, columnspan=4, sticky="ew", pady=10)
        
        gcp_top_frame = tk.Frame(frame_1)
        gcp_top_frame.grid(row=3, column=0, columnspan=3, sticky="w", pady=(0,5))
        
        tk.Checkbutton(gcp_top_frame, text=self.t["gcp_chk"], variable=self.use_gcp, font=self.font_normal, fg="#D35400", command=self.toggle_gcp_state).pack(side=tk.LEFT)
        
        self.btn_gcp_help = tk.Button(gcp_top_frame, text=self.t["btn_gcp_help"], font=self.font_tiny, command=self.show_gcp_help)
        self.btn_gcp_help.pack(side=tk.LEFT, padx=10)

        self.btn_gcp_tutorial = tk.Button(gcp_top_frame, text=self.t["btn_gcp_tutorial"], font=self.font_tiny, command=self.show_gcp_tutorial)
        self.btn_gcp_tutorial.pack(side=tk.LEFT, padx=(0, 10))
        
        self.lbl_gcp = tk.Label(frame_1, text=self.t["gcp_lbl"], font=self.font_normal)
        self.lbl_gcp.grid(row=4, column=0, sticky="w", pady=5)
        
        self.entry_gcp = tk.Entry(frame_1, textvariable=self.gcp_path, font=self.font_normal, state='readonly', width=38)
        self.entry_gcp.grid(row=4, column=1, padx=5)
        
        self.btn_gcp = tk.Button(frame_1, text=self.t["btn_browse"], font=self.font_normal, command=self.browse_gcp)
        self.btn_gcp.grid(row=4, column=2)

        frame_2 = tk.LabelFrame(left_frame, text=self.t["step2_title"], font=self.font_title, fg="#2E86C1", padx=10, pady=10)
        frame_2.pack(fill=tk.X, pady=(0, 10))
        tk.Radiobutton(frame_2, text=self.t["mode_fast"], variable=self.mode_var, value="fast", font=self.font_normal).pack(anchor=tk.W, pady=2)
        tk.Radiobutton(frame_2, text=self.t["mode_high"], variable=self.mode_var, value="high", font=self.font_normal).pack(anchor=tk.W, pady=2)
        tk.Radiobutton(frame_2, text=self.t["mode_huge"], variable=self.mode_var, value="huge", font=self.font_normal, fg="#D35400").pack(anchor=tk.W, pady=2)

        frame_3 = tk.Frame(left_frame)
        frame_3.pack(fill=tk.X, pady=(5, 5))
        self.btn_start = tk.Button(frame_3, text=self.t["btn_start"], font=(self.font_title[0], 13, "bold"), 
                                   bg="#4CAF50", fg="white", command=self.start_processing_thread, height=2)
        self.btn_start.pack(fill=tk.X, pady=(0, 10))

        progress_frame = tk.Frame(frame_3)
        progress_frame.pack(fill=tk.X)
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.time_label = tk.Label(progress_frame, text=f"{self.t['time_elapsed']}00:00:00", font=("Consolas", 11, "bold"), fg="#555555")
        self.time_label.pack(side=tk.RIGHT)

        tk.Label(left_frame, text=self.t["log_lbl"], font=self.font_title).pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(left_frame, font=("Consolas", 9), bg="#1E1E1E", fg="#00FF00")
        self.log_area.pack(fill=tk.BOTH, expand=True)

        map_top_frame = tk.Frame(right_frame)
        map_top_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(map_top_frame, text=self.t["map_lbl"], font=self.font_title, fg="#27AE60").pack(side=tk.LEFT)
        
        self.btn_fit = ttk.Button(map_top_frame, text=self.t["map_btn_fit"], command=self.fit_map_bounds)
        self.btn_fit.pack(side=tk.RIGHT, padx=(5, 0))

        self.map_style = tk.StringVar(value=self.t["map_g_sat"])
        style_combo = ttk.Combobox(map_top_frame, textvariable=self.map_style, state="readonly", width=25)
        style_combo['values'] = (self.t["map_osm"], self.t["map_g_sat"], self.t["map_g_nor"])
        style_combo.pack(side=tk.RIGHT)
        style_combo.bind("<<ComboboxSelected>>", self.change_map_style)

        self.map_widget = tkintermapview.TkinterMapView(right_frame, corner_radius=0)
        self.map_widget.pack(fill=tk.BOTH, expand=True)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def show_gcp_tutorial(self):
        tut_win = tk.Toplevel(self.root)
        tut_win.title(self.t["gcp_tut_title"])
        tut_win.geometry("650x550")
        tut_win.grab_set()

        txt_widget = scrolledtext.ScrolledText(tut_win, font=self.font_normal, wrap=tk.WORD)
        txt_widget.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
        txt_widget.insert(tk.END, self.t["gcp_tut_text"])
        txt_widget.config(state=tk.DISABLED)

        btn_close = tk.Button(tut_win, text=self.t["btn_close"], font=self.font_title, command=tut_win.destroy)
        btn_close.pack(pady=(0, 15))

    def show_gcp_help(self):
        help_win = tk.Toplevel(self.root)
        help_win.title(self.t["gcp_help_title"])
        help_win.geometry("580x420")
        help_win.grab_set() 

        txt_widget = scrolledtext.ScrolledText(help_win, font=self.font_normal, wrap=tk.WORD, height=14)
        txt_widget.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
        txt_widget.insert(tk.END, self.t["gcp_help_text"])
        txt_widget.config(state=tk.DISABLED)

        btn_frame = tk.Frame(help_win)
        btn_frame.pack(pady=(0, 15))

        def download_template():
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile="gcp_template.txt",
                title=self.t["gcp_dl_title"],
                filetypes=[("Text files", "*.txt")]
            )
            if filepath:
                # 🌟 寫入 NewGCP1.txt 的正確範本內容
                template_content = """EPSG:3826
208338.079 2610073.274 365.692 2971 412 MAX_0488.JPG no1
208338.079 2610073.274 365.692 5388 2032 MAX_0490.JPG no1
208338.079 2610073.274 365.692 3590 1787 MAX_0499.JPG no1
208321.384 2610011.857 370.119 1527 511 MAX_0502.JPG no2
208321.384 2610011.857 370.119 1994 1602 MAX_0519.JPG no2
208321.384 2610011.857 370.119 1952 2303 MAX_0520.JPG no2
208311.135 2609976.758 380.817 2699 2116 MAX_0518.JPG no3
208311.135 2609976.758 380.817 3912 2234 MAX_0536.JPG no3
208311.135 2609976.758 380.817 3852 2995 MAX_0537.JPG no3
208315.507 2609880.947 418.195 3704 2488 MAX_0547.JPG no4
208315.507 2609880.947 418.195 358 318 MAX_0548.JPG no4
208315.507 2609880.947 418.195 3806 1246 MAX_0546.JPG no4
208380.064 2610022.495 372.364 3118 1879 MAX_0522.JPG no5
208380.064 2610022.495 372.364 3396 2398 MAX_0532.JPG no5
208380.064 2610022.495 372.364 3501 966 MAX_0530.JPG no5
"""
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(template_content)
                    messagebox.showinfo(self.t["msg_success_title"], self.t["msg_gcp_dl_success"].format(filepath=filepath), parent=help_win)
                except Exception as e:
                    messagebox.showerror(self.t["msg_err_title"], self.t["msg_gcp_dl_err"].format(e=e), parent=help_win)

        btn_download = tk.Button(btn_frame, text=self.t["btn_gcp_dl"], font=self.font_title, bg="#3498DB", fg="white", command=download_template)
        btn_download.pack(side=tk.LEFT, padx=10)
        
        btn_close = tk.Button(btn_frame, text=self.t["btn_close"], font=self.font_title, command=help_win.destroy)
        btn_close.pack(side=tk.LEFT, padx=10)

    def toggle_gcp_state(self):
        state = tk.NORMAL if self.use_gcp.get() else tk.DISABLED
        fg_color = "black" if self.use_gcp.get() else "gray"
        self.lbl_gcp.config(fg=fg_color)
        self.entry_gcp.config(state=state if self.use_gcp.get() else 'readonly')
        self.btn_gcp.config(state=state)
        
        if not self.use_gcp.get():
            self.entry_gcp.config(state=tk.NORMAL)
            self.gcp_path.set("")
            self.entry_gcp.config(state='readonly')
            self.clear_gcp_markers()

    def change_map_style(self, event=None):
        style = self.map_style.get()
        if style == self.t["map_osm"]: self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif style == self.t["map_g_sat"]: self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif style == self.t["map_g_nor"]: self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def fit_map_bounds(self):
        lats = [m.position[0] for m in self.photo_markers.values()] + [m.position[0] for m in self.gcp_markers.values()]
        lons = [m.position[1] for m in self.photo_markers.values()] + [m.position[1] for m in self.gcp_markers.values()]
        
        if not lats or not lons: return
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        lat_margin = (max_lat - min_lat) * 0.1 if max_lat != min_lat else 0.001
        lon_margin = (max_lon - min_lon) * 0.1 if max_lon != min_lon else 0.001
        self.map_widget.fit_bounding_box(
            (max_lat + lat_margin, min_lon - lon_margin), 
            (min_lat - lat_margin, max_lon + lon_margin)
        )

    def get_exif_gps(self, filepath):
        def _get_if_exist(data, key): return data.get(key)
        def _convert_to_degrees(value): return float(value[0]) + (float(value[1]) / 60.0) + (float(value[2]) / 3600.0)
        try:
            image = Image.open(filepath)
            exif = image._getexif()
            if not exif: return None, None
            gps_info = {}
            for key, value in exif.items():
                if TAGS.get(key, key) == "GPSInfo":
                    for t in value: gps_info[GPSTAGS.get(t, t)] = value[t]
            lat_data = _get_if_exist(gps_info, "GPSLatitude")
            lat_ref = _get_if_exist(gps_info, "GPSLatitudeRef")
            lon_data = _get_if_exist(gps_info, "GPSLongitude")
            lon_ref = _get_if_exist(gps_info, "GPSLongitudeRef")
            if lat_data and lat_ref and lon_data and lon_ref:
                lat = _convert_to_degrees(lat_data)
                if lat_ref != "N": lat = -lat
                lon = _convert_to_degrees(lon_data)
                if lon_ref != "E": lon = -lon
                return lat, lon
        except Exception: return None, None
        return None, None

    def browse_source(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            norm_path = os.path.normpath(folder_selected)
            self.source_path.set(norm_path)
            if not self.output_path.get(): self.output_path.set(f"{norm_path}_Results")
            threading.Thread(target=self.load_photos_to_map, args=(norm_path,), daemon=True).start()

    def browse_output(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_path.set(os.path.normpath(folder_selected))

    def browse_gcp(self):
        file_selected = filedialog.askopenfilename(filetypes=[("Text files", "*.txt;*.csv"), ("All files", "*.*")])
        if file_selected:
            self.entry_gcp.config(state=tk.NORMAL)
            self.gcp_path.set(os.path.normpath(file_selected))
            self.entry_gcp.config(state='readonly')
            self.load_gcp_to_map(file_selected)

    def clear_gcp_markers(self):
        for marker in self.gcp_markers.values(): marker.delete()
        self.gcp_markers.clear()

    def load_gcp_to_map(self, filepath):
        self.clear_gcp_markers()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines: return
            
            epsg_line = lines[0].strip().upper()
            source_epsg = "EPSG:4326"
            if "EPSG:" in epsg_line:
                match = re.search(r'EPSG:(\d+)', epsg_line)
                if match:
                    source_epsg = f"EPSG:{match.group(1)}"
            
            is_wgs84 = source_epsg == "EPSG:4326"
            
            transformer = None
            if not is_wgs84:
                self.safe_print(self.t.get("log_gcp_transform", "🔄 Detected non-WGS84...").format(epsg=source_epsg))
                try:
                    transformer = pyproj.Transformer.from_crs(source_epsg, "EPSG:4326", always_xy=True)
                except Exception as e:
                    self.safe_print(self.t.get("log_gcp_transform_err", "⚠️ Error...").format(e=e))
                    return
                
            count = 0
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) >= 6:
                    try:
                        raw_x = float(parts[0]) 
                        raw_y = float(parts[1]) 
                        gcp_name = parts[6] if len(parts) >= 7 else f"GCP_{count}"
                        
                        if transformer:
                            lon, lat = transformer.transform(raw_x, raw_y)
                        else:
                            lon, lat = raw_x, raw_y
                        
                        marker = self.map_widget.set_marker(
                            lat, lon, 
                            text=gcp_name, 
                            icon=self.icon_triangle,
                            text_color="#000000", font=self.font_tiny
                        )
                        self.gcp_markers[f"gcp_{count}"] = marker
                        count += 1
                    except Exception:
                        pass
            
            if self.gcp_markers:
                self.fit_map_bounds()
                self.safe_print(self.t["log_gcp_loaded"].format(count=len(self.gcp_markers)))
                
        except Exception as e:
            self.safe_print(self.t["log_gcp_parse_err"].format(e=e))

    def check_map_zoom(self):
        try:
            if self.map_widget.winfo_exists():
                current_zoom = self.map_widget.zoom
                should_show = current_zoom >= 17
                
                if self.marker_text_visible != should_show:
                    self.marker_text_visible = should_show
                    for marker in self.photo_markers.values():
                        marker.text = getattr(marker, 'real_text', '') if should_show else None
                        marker.draw()
        except Exception:
            pass
        self.root.after(500, self.check_map_zoom)

    def load_photos_to_map(self, folder):
        for marker in self.photo_markers.values(): marker.delete()
        self.photo_markers.clear()
        
        self.safe_print(self.t["log_scan_gps"])
        
        for file in os.listdir(folder):
            if file.lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff')):
                filepath = os.path.join(folder, file)
                lat, lon = self.get_exif_gps(filepath)
                if lat and lon:
                    marker = self.map_widget.set_marker(
                        lat, lon, 
                        text=file if self.marker_text_visible else None, 
                        icon=self.icon_green,
                        text_color="#FFFF00", font=self.font_tiny
                    )
                    marker.process_status = "green" 
                    marker.real_text = file  
                    self.photo_markers[file] = marker
        
        if self.photo_markers:
            self.fit_map_bounds()
            self.safe_print(self.t["log_photo_loaded"].format(count=len(self.photo_markers)))
        else:
            self.safe_print(self.t["log_no_gps"])

    def process_ui_updates(self):
        try:
            if not self.root.winfo_exists(): return
        except Exception: return

        lines = []
        try:
            while not self.log_queue.empty():
                lines.append(self.log_queue.get_nowait())
                if len(lines) > 200: break  
        except Exception: pass
        
        if lines:
            try:
                self.log_area.insert(tk.END, "".join(lines))
                self.log_area.see(tk.END)
            except Exception: pass

        try:
            processed_markers = set()
            while not self.marker_queue.empty():
                processed_markers.add(self.marker_queue.get_nowait())
            
            for filename in processed_markers:
                if filename in self.photo_markers:
                    old_marker = self.photo_markers[filename]
                    
                    current_status = getattr(old_marker, "process_status", "green")
                    
                    if current_status == "green":
                        new_status = "red"
                        new_icon = self.icon_red
                    else:
                        new_status = "green"
                        new_icon = self.icon_green
                        
                    pos = old_marker.position
                    real_text = getattr(old_marker, "real_text", filename)
                    old_marker.delete()
                    
                    new_marker = self.map_widget.set_marker(
                        pos[0], pos[1], 
                        text=real_text if self.marker_text_visible else None, 
                        icon=new_icon, text_color="#FFFF00", font=self.font_tiny
                    )
                    new_marker.process_status = new_status
                    new_marker.real_text = real_text
                    self.photo_markers[filename] = new_marker 
        except Exception: pass

        self.root.after(100, self.process_ui_updates)

    def safe_print(self, text):
        self.log_queue.put(text)

    def check_nvidia_gpu(self):
        try:
            subprocess.run(["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except: return False

    def check_docker_engine(self):
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            return True
        except: return False

    def start_docker_desktop(self):
        docker_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if os.path.exists(docker_path):
            try:
                subprocess.Popen([docker_path], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                return True
            except: return False
        return False

    def optimize_wsl_memory(self):
        if os.name != 'nt': return False
        try:
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

            total_ram_gb = stat.ullTotalPhys / (1024**3)
            target_ram = max(8, int(total_ram_gb * 0.8))
            target_swap = target_ram * 2

            wslconfig_path = os.path.join(os.path.expanduser("~"), ".wslconfig")
            config_content = f"[wsl2]\nmemory={target_ram}GB\nswap={target_swap}GB\n"

            if os.path.exists(wslconfig_path):
                with open(wslconfig_path, 'r', encoding='utf-8') as f:
                    if "memory=" in f.read(): return False

            self.safe_print(self.t["log_wsl_fix"])
            with open(wslconfig_path, 'w', encoding='utf-8') as f: f.write(config_content)
            subprocess.run(["wsl", "--shutdown"], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.safe_print(self.t["log_wsl_done"])
            time.sleep(2)
            return True
        except Exception: return False

    def update_timer(self):
        try:
            if self.is_running and self.start_time and self.time_label.winfo_exists():
                elapsed = int(time.time() - self.start_time)
                td = datetime.timedelta(seconds=elapsed)
                self.time_label.config(text=f"{self.t['time_elapsed']}{td}")
                self.root.after(1000, self.update_timer)
        except Exception:
            pass

    def start_processing_thread(self):
        if not self.source_path.get() or not self.output_path.get():
            messagebox.showwarning("Warning", self.t["msg_err_folder"])
            return
        
        if self.use_gcp.get() and not self.gcp_path.get():
            messagebox.showwarning("Warning", self.t["msg_err_gcp"])
            return
            
        self.btn_start.config(state=tk.DISABLED, text=self.t["btn_init"], bg="#888888")
        self.log_area.delete(1.0, tk.END)
        self.progress_bar.start(15)
        
        self.start_time = time.time()
        self.is_running = True
        self.update_timer()
        
        threading.Thread(target=self.run_odm, daemon=True).start()

    def run_odm(self):
        source_dir = self.source_path.get()
        output_dir = self.output_path.get()
        mode = self.mode_var.get()
        gcp_file = self.gcp_path.get() if self.use_gcp.get() else None
        
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        self.safe_print("="*60 + "\n")
        self.safe_print(f"📷 SOURCE: {source_dir}\n")
        self.safe_print(f"🎯 OUTPUT: {output_dir}\n")
        if gcp_file: self.safe_print(f"📍 GCP: {gcp_file}\n")
        self.safe_print("="*60 + "\n")

        docker_gcp_path = None
        if gcp_file and os.path.exists(gcp_file):
            try:
                dest_gcp = os.path.join(output_dir, "gcp_list.txt")
                shutil.copy2(gcp_file, dest_gcp)
                docker_gcp_path = "/datasets/project/gcp_list.txt"
                self.safe_print(self.t["log_gcp_yes"])
            except Exception as e:
                self.safe_print(self.t["log_gcp_copy_err"].format(e=e))
                docker_gcp_path = None

        self.optimize_wsl_memory()

        self.safe_print(self.t["log_start_chk"])
        if not self.check_docker_engine():
            self.safe_print(self.t["log_docker_sleep"])
            if self.start_docker_desktop():
                self.safe_print(self.t["log_docker_wait"])
                engine_ready = False
                for i in range(40):
                    time.sleep(3)
                    self.safe_print(". ")
                    if self.check_docker_engine():
                        engine_ready = True
                        break
                self.safe_print("\n")
                if not engine_ready:
                    self.safe_print(self.t["log_docker_fail"])
                    self.reset_ui()
                    return
                self.safe_print(self.t["log_docker_ready"])
            else:
                 self.safe_print(self.t["log_docker_err"])
                 self.reset_ui()
                 return

        self.safe_print(self.t["log_gpu_chk"])
        has_gpu = self.check_nvidia_gpu()

        odm_image = "opendronemap/odm:gpu" if has_gpu else "opendronemap/odm:latest"
        
        command = ["docker", "run", "--rm"]
        if has_gpu:
            self.safe_print(self.t["log_gpu_yes"])
            command.extend(["--gpus", "all"])

        odm_params = [
            "--project-path", "/datasets", "project",
            "--dsm", "--orthophoto-compression", "LZW", "--skip-report",
            "--ignore-gsd", "--auto-boundary",
            "--rerun-all"
        ]

        if docker_gcp_path:
            odm_params.extend(["--gcp", docker_gcp_path])

        if mode == "fast":
            odm_params.extend(["--fast-orthophoto", "--max-concurrency", "14"])
        elif mode == "high":
            odm_params.extend(["--pc-quality", "medium", "--dem-resolution", "5", "--max-concurrency", "2", "--pc-filter", "2.5"])
        elif mode == "huge":
            odm_params.extend([
                "--split", "120",              
                "--split-overlap", "60",      
                "--feature-quality", "low",    
                "--min-num-features", "8000",
                "--pc-quality", "low",
                "--dem-resolution", "10",
                "--max-concurrency", "2",
                "--force-gps",
                "--crop", "15"
            ])

        py_patch_code = """
import os, re
f='/code/opendm/cutline.py'
if os.path.exists(f):
    c = open(f).read()
    c = re.sub(r'mapping\\(([^)]+)\\)', r'({"type": "MultiPolygon", "coordinates": [mapping(\\1)["coordinates"]]} if getattr(\\1, "geom_type", "") == "Polygon" else mapping(\\1))', c)
    open(f, 'w').write(c)
"""
        patch_b64 = base64.b64encode(py_patch_code.encode('utf-8')).decode('utf-8')
        
        param_str = " ".join(odm_params)
        run_script = f"source /code/venv/bin/activate && pip install -q 'numpy<2' && echo {patch_b64} | base64 -d | python && python /code/run.py {param_str}"

        command.extend([
            "-v", f"{output_dir}:/datasets/project", 
            "-v", f"{source_dir}:/datasets/project/images:ro", 
            "--entrypoint", "/bin/bash",
            odm_image,  
            "-c", run_script             
        ])

        self.safe_print(self.t["log_odm_start"])

        try:
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            self.process_handle = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace', creationflags=creationflags
            )

            for line in self.process_handle.stdout:
                self.safe_print(line)
                
                match = re.search(r'([A-Za-z0-9_.-]+\.(?:jpg|JPG|jpeg|JPEG|tif|TIF|tiff|TIFF))', line)
                if match:
                    self.marker_queue.put(match.group(1))

            self.process_handle.wait()

            if self.process_handle.returncode == 0:
                self.safe_print("\n" + "="*60 + "\n")
                self.safe_print(self.t["log_clean_start"])
                time.sleep(2) 
                
                keep_list = ["odm_dem", "odm_orthophoto"]
                try:
                    for item in os.listdir(output_dir):
                        if item not in keep_list:
                            item_path = os.path.join(output_dir, item)
                            if os.path.isdir(item_path): shutil.rmtree(item_path)
                            else: os.remove(item_path)
                    self.safe_print(self.t["log_clean_done"])
                except Exception: pass

                self.safe_print(self.t["log_done"])
                self.safe_print("="*60 + "\n")
                
                try:
                    final_time = self.time_label.cget('text').replace(self.t["time_elapsed"], "")
                    msg = self.t["msg_done_body"].format(time=final_time, path=output_dir)
                    messagebox.showinfo(self.t["msg_done_title"], msg)
                except Exception: pass
            else:
                if self.is_running:
                    try:
                        msg = self.t["msg_err_body"].format(code=self.process_handle.returncode)
                        messagebox.showerror(self.t["msg_err_title"], msg)
                    except Exception: pass

        except Exception as e:
            if self.is_running:
                self.safe_print(self.t["log_exception"].format(e=e))
        finally:
            self.reset_ui()

    def reset_ui(self):
        self.is_running = False
        self.process_handle = None
        try:
            if self.progress_bar.winfo_exists():
                self.progress_bar.stop() 
        except Exception: pass
        def update_btn():
            try:
                if self.btn_start.winfo_exists():
                    self.btn_start.config(state=tk.NORMAL, text=self.t["btn_start"], bg="#4CAF50")
            except Exception: pass
        try:
            self.root.after(0, update_btn)
        except Exception: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DroneProcessingApp(root)
    root.mainloop()
