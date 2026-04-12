import sys
import subprocess
import queue
import base64

# ==========================================
# 🛡️ 核心新功能：自動偵測與安裝必備套件
# ==========================================
def check_and_install_packages():
    missing_packages = []
    try: import tkintermapview
    except ImportError: missing_packages.append("tkintermapview")
    try: import PIL
    except ImportError: missing_packages.append("Pillow")
        
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
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk 
import tkintermapview
from PIL import Image, ImageDraw, ImageTk 
from PIL.ExifTags import TAGS, GPSTAGS

LANG = {
    "en": {
        "title": "🚁 Drone Mapping Auto-Processor (Pro Ultimate GIS Edition)",
        "step1_title": " 📂 Step 1: Set Folders ",
        "src_lbl": "Source Photos:",
        "out_lbl": "Output Folder:",
        "btn_browse": "Browse...",
        "step2_title": " ⚙️ Step 2: Choose Mode ",
        "mode_fast": "⚡Fast Orthophoto - Skips 3D point cloud, extremely fast",
        "mode_high": "🏗 High Precision - Detailed DSM & 3D model (< 300 imgs)",
        "mode_huge": "🗺 Huge Dataset - Split processing, prevents OOM (> 500 imgs)",
        "btn_start": "🚀 Start Auto Processing",
        "btn_init": "⚙️ System initializing...",
        "time_elapsed": "⏳ Elapsed: ",
        "log_lbl": "📜 Execution Log:",
        "map_lbl": "🗺 UAV Flight Path & Status Map",
        "map_osm": "OpenStreetMap (Standard)",
        "map_g_sat": "Google Maps (Satellite)",
        "map_g_nor": "Google Maps (Roadmap)",
        "map_btn_fit": "🔍 Fit to All",
        "msg_err_folder": "Please set both Source and Output folders!",
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
        "log_odm_start": "\n--- 🏁 Calling ODM Engine, processing started ---\n\n",
        "log_clean_start": "🧹 Cleaning up temporary files...\n",
        "log_clean_done": "✨ Cleanup complete! Only orthophoto and DSM are kept.\n",
        "log_done": "✅ Processing completed successfully!\n",
        "msg_done_title": "Completed",
        "msg_done_body": "Processing and cleanup successful!\nTime: {time}\nSaved at:\n{path}",
        "msg_err_title": "Error",
        "msg_err_body": "Processing failed (Code: {code})\nPlease check the log."
    },
    "zh": {
        "title": "🚁 航測影像自動化處理工具 (Pro 地圖即時監控版)",
        "step1_title": " 📂 第一步：設定資料夾 ",
        "src_lbl": "原始照片：",
        "out_lbl": "輸出結果：",
        "btn_browse": "瀏覽...",
        "step2_title": " ⚙️ 第二步：選擇處理模式 ",
        "mode_fast": "⚡快速地圖模式 (Fast Orthophoto) - 略過點雲，速度極快",
        "mode_high": "🏗 高精度重建模式 (High Precision) - 產出細緻 3D (<300張)",
        "mode_huge": "🗺 超大範圍切割模式 (Huge Dataset) - 產出細緻 3D (>300張)",
        "btn_start": "🚀 開始全自動處理",
        "btn_init": "⚙️ 系統初始化中...",
        "time_elapsed": "⏳ 經過時間：",
        "log_lbl": "📜 執行監控 (Log)：",
        "map_lbl": "🗺 航線位置與即時進度圖",
        "map_osm": "開源地圖 (OpenStreetMap)",
        "map_g_sat": "Google 衛星地圖",
        "map_g_nor": "Google 標準地圖",
        "map_btn_fit": "🔍 顯示所有範圍",
        "msg_err_folder": "請先設定「原始照片」與「輸出結果」的資料夾！",
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
        "log_odm_start": "\n--- 🏁 呼叫 ODM Engine，開始運算 ---\n\n",
        "log_clean_start": "🧹 開始清理不必要的暫存檔案...\n",
        "log_clean_done": "✨ 清理完成！已刪除暫存檔，僅保留最終成果。\n",
        "log_done": "✅ 處理成功完成！請至「輸出資料夾」查看結果。\n",
        "msg_done_title": "完成",
        "msg_done_body": "運算與清理皆已成功完成！\n耗時：{time}\n檔案已存於：\n{path}",
        "msg_err_title": "錯誤",
        "msg_err_body": "運算失敗 (代碼: {code})\n請查看 Log 了解詳細原因。"
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
        
        self.start_time = None
        self.is_running = False
        self.photo_markers = {}
        self.process_handle = None
        
        # UI 非同步佇列防當機機制
        self.log_queue = queue.Queue()
        self.marker_queue = queue.Queue()
        
        # LOD 顯示控制變數
        self.marker_text_visible = True
        
        # 🌟 繪製 10像素 圓點 (維持純圓形，尺寸放大至 10)
        self.icon_green = self.create_circle_icon("#2ECC71", "#1E8449", 10)
        self.icon_red = self.create_circle_icon("#E74C3C", "#922B21", 10)
        
        self.create_widgets()
        
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

    def create_widgets(self):
        left_frame = tk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_frame = tk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        frame_1 = tk.LabelFrame(left_frame, text=self.t["step1_title"], font=self.font_title, fg="#2E86C1", padx=10, pady=10)
        frame_1.pack(fill=tk.X, pady=(0, 10))
        tk.Label(frame_1, text=self.t["src_lbl"], font=self.font_normal).grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(frame_1, textvariable=self.source_path, font=self.font_normal, state='readonly', width=40).grid(row=0, column=1, padx=5)
        tk.Button(frame_1, text=self.t["btn_browse"], font=self.font_normal, command=self.browse_source).grid(row=0, column=2)
        tk.Label(frame_1, text=self.t["out_lbl"], font=self.font_normal).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(frame_1, textvariable=self.output_path, font=self.font_normal, state='readonly', width=40).grid(row=1, column=1, padx=5)
        tk.Button(frame_1, text=self.t["btn_browse"], font=self.font_normal, command=self.browse_output).grid(row=1, column=2)

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

    def change_map_style(self, event=None):
        style = self.map_style.get()
        if style == self.t["map_osm"]: self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif style == self.t["map_g_sat"]: self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif style == self.t["map_g_nor"]: self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def fit_map_bounds(self):
        if not self.photo_markers: return
        lats = [m.position[0] for m in self.photo_markers.values()]
        lons = [m.position[1] for m in self.photo_markers.values()]
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

    # 🌟 LOD 偵測器：根據 Zoom Level 動態控制文字顯示
    def check_map_zoom(self):
        try:
            if self.photo_markers and self.map_widget.winfo_exists():
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
        
        self.safe_print("🗺️ 正在掃描照片 GPS 座標...\n")
        
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
            self.safe_print(f"✅ 成功標定 {len(self.photo_markers)} 張照片於地圖。\n")
        else:
            self.safe_print("⚠️ 未找到具備 GPS 座標的照片。\n")

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
                    
                    # 🌟 狀態切換邏輯 (綠 <-> 紅)
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
        
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        self.safe_print("="*60 + "\n")
        self.safe_print(f"📷 SOURCE: {source_dir}\n")
        self.safe_print(f"🎯 OUTPUT: {output_dir}\n")
        self.safe_print("="*60 + "\n")

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
                "--pc-quality", "lowest",
                "--dem-resolution", "10",
                "--max-concurrency", "2",
                "--pc-filter", "2.5",     
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
                self.safe_print(f"\n❌ Exception: {e}\n")
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
