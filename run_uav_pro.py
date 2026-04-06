import os
import subprocess
import threading
import time
import datetime
import shutil
import locale
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk 

LANG = {
    "en": {
        "title": "🚁 Drone Mapping Auto-Processor (Pro Ultimate)",
        "step1_title": " 📂 Step 1: Set Folders ",
        "src_lbl": "Source Photos Folder (Read-only):",
        "out_lbl": "Output Folder (Orthophoto, DSM):",
        "btn_browse": "Browse...",
        "step2_title": " ⚙️ Step 2: Choose Processing Mode ",
        "mode_fast": "⚡ Fast Orthophoto - Skips dense point cloud, extremely fast",
        "mode_high": "🏗️ High Precision - Detailed DSM & 3D model (Recommended < 300 imgs)",
        "mode_huge": "🗺️ Huge Dataset - Split processing, prevents OOM (> 500 imgs)",
        "btn_start": "🚀 Start Auto Processing",
        "btn_init": "⚙️ System initializing...",
        "time_elapsed": "⏳ Elapsed Time: ",
        "log_lbl": "📜 Execution Log:",
        "msg_err_folder": "Please set both Source and Output folders!",
        "log_wsl_fix": "🔧 Auto-configuring Windows WSL2 memory limits to prevent OOM crashes...\n",
        "log_wsl_done": "✅ WSL2 memory limits optimized! Restarting Docker engine...\n",
        "log_start_chk": "🐳 Checking Docker engine status...\n",
        "log_docker_sleep": "💤 Docker is sleeping, attempting to wake up...\n",
        "log_docker_wait": "⏳ Waiting for Docker to warm up (approx. 1-2 mins)\n",
        "log_docker_ready": "✅ Docker engine is ready! Taking over the task.\n\n",
        "log_docker_fail": "❌ Timeout! Cannot confirm Docker status. Please open Docker Desktop manually.\n",
        "log_docker_err": "❌ Failed to auto-start Docker. Please open it manually.\n",
        "log_gpu_chk": "🔍 Detecting GPU hardware...\n",
        "log_gpu_yes": "🌟 NVIDIA GPU detected, switching to CUDA dedicated engine!\n",
        "log_odm_start": "\n--- 🏁 Calling ODM Engine, processing started ---\n\n",
        "log_clean_start": "🧹 Cleaning up temporary files to free up disk space...\n",
        "log_clean_done": "✨ Cleanup complete! Only final orthophoto and DSM are kept.\n",
        "log_done": "✅ Processing completed successfully! Check the output folder.\n",
        "msg_done_title": "Completed",
        "msg_done_body": "Processing and cleanup successful!\nTime: {time}\nSaved at:\n{path}",
        "msg_err_title": "Error",
        "msg_err_body": "Processing failed (Code: {code})\nPlease check the log for details."
    },
    "zh": {
        "title": "🚁 航測影像自動化處理工具 (Pro 專業終極版)",
        "step1_title": " 📂 第一步：設定資料夾 ",
        "src_lbl": "原始照片資料夾 (僅讀取，不修改)：",
        "out_lbl": "結果輸出資料夾 (正射影像、DSM)：",
        "btn_browse": "瀏覽...",
        "step2_title": " ⚙️ 第二步：選擇處理模式 ",
        "mode_fast": "⚡ 快速地圖模式 (Fast Orthophoto) - 略過密集點雲，速度極快",
        "mode_high": "🏗️ 高精度重建模式 (High Precision) - 產出細緻 DSM 與 3D 模型",
        "mode_huge": "🗺️ 超大範圍切割模式 (Huge Dataset) - 防記憶體崩潰，分塊處理",
        "btn_start": "🚀 開始全自動處理",
        "btn_init": "⚙️ 系統初始化中...",
        "time_elapsed": "⏳ 經過時間：",
        "log_lbl": "📜 執行監控 (Log)：",
        "msg_err_folder": "請先設定「原始照片」與「輸出結果」的資料夾！",
        "log_wsl_fix": "🔧 正在自動解除 Windows WSL2 記憶體封印，防止運算崩潰...\n",
        "log_wsl_done": "✅ 記憶體封印解除成功！強制重啟底層引擎...\n",
        "log_start_chk": "🐳 正在檢查 Docker 引擎狀態...\n",
        "log_docker_sleep": "💤 Docker 正在沉睡，嘗試發送喚醒指令...\n",
        "log_docker_wait": "⏳ 正在等待 Docker 暖機 (通常需要 1 到 2 分鐘，請喝口茶)\n",
        "log_docker_ready": "✅ Docker 引擎暖機完畢！接管任務。\n\n",
        "log_docker_fail": "❌ 等待逾時！無法確認 Docker 狀態，請手動從開始選單開啟 Docker Desktop。\n",
        "log_docker_err": "❌ 無法自動啟動 Docker，請手動開啟。\n",
        "log_gpu_chk": "🔍 正在偵測 GPU 硬體環境...\n",
        "log_gpu_yes": "🌟 偵測到 NVIDIA GPU，切換至 CUDA 專用版引擎！\n",
        "log_odm_start": "\n--- 🏁 呼叫 ODM 引擎，開始運算 ---\n\n",
        "log_clean_start": "🧹 開始清理不必要的暫存檔案，釋放硬碟空間...\n",
        "log_clean_done": "✨ 清理完成！已為您刪除所有暫存檔，僅保留最終成果。\n",
        "log_done": "✅ 處理成功完成！請至「輸出資料夾」查看結果。\n",
        "msg_done_title": "完成",
        "msg_done_body": "運算與清理皆已成功完成！\n耗時：{time}\n\n檔案已存於：\n{path}",
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
                if lang_id in [1028, 2052, 3076, 4100, 5124]:
                    self.lang_code = "zh"
            else:
                sys_lang = str(locale.getlocale()[0]).lower()
                if "zh" in sys_lang or "chinese" in sys_lang or "tw" in sys_lang:
                    self.lang_code = "zh"
        except Exception:
            pass

        self.t = LANG[self.lang_code]

        self.root.title(self.t["title"])
        self.root.geometry("800x750")
        self.root.configure(padx=20, pady=15)
        
        self.font_title = ("微軟正黑體", 12, "bold") if self.lang_code == "zh" else ("Segoe UI", 11, "bold")
        self.font_normal = ("微軟正黑體", 10) if self.lang_code == "zh" else ("Segoe UI", 10)
        
        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.mode_var = tk.StringVar(value="fast") 
        
        self.start_time = None
        self.is_running = False
        
        self.create_widgets()

    def create_widgets(self):
        frame_1 = tk.LabelFrame(self.root, text=self.t["step1_title"], font=self.font_title, fg="#2E86C1", padx=10, pady=10)
        frame_1.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame_1, text=self.t["src_lbl"], font=self.font_normal).grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(frame_1, textvariable=self.source_path, font=self.font_normal, state='readonly', width=45).grid(row=0, column=1, padx=5)
        tk.Button(frame_1, text=self.t["btn_browse"], font=self.font_normal, command=self.browse_source, width=8).grid(row=0, column=2)

        tk.Label(frame_1, text=self.t["out_lbl"], font=self.font_normal).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(frame_1, textvariable=self.output_path, font=self.font_normal, state='readonly', width=45).grid(row=1, column=1, padx=5)
        tk.Button(frame_1, text=self.t["btn_browse"], font=self.font_normal, command=self.browse_output, width=8).grid(row=1, column=2)

        frame_2 = tk.LabelFrame(self.root, text=self.t["step2_title"], font=self.font_title, fg="#2E86C1", padx=10, pady=10)
        frame_2.pack(fill=tk.X, pady=(0, 10))

        tk.Radiobutton(frame_2, text=self.t["mode_fast"], variable=self.mode_var, value="fast", font=self.font_normal).pack(anchor=tk.W, pady=2)
        tk.Radiobutton(frame_2, text=self.t["mode_high"], variable=self.mode_var, value="high", font=self.font_normal).pack(anchor=tk.W, pady=2)
        tk.Radiobutton(frame_2, text=self.t["mode_huge"], variable=self.mode_var, value="huge", font=self.font_normal, fg="#D35400").pack(anchor=tk.W, pady=2)

        frame_3 = tk.Frame(self.root)
        frame_3.pack(fill=tk.X, pady=(5, 5))

        self.btn_start = tk.Button(frame_3, text=self.t["btn_start"], font=(self.font_title[0], 13, "bold"), 
                                   bg="#4CAF50", fg="white", command=self.start_processing_thread, height=2)
        self.btn_start.pack(fill=tk.X, pady=(0, 10))

        progress_frame = tk.Frame(frame_3)
        progress_frame.pack(fill=tk.X)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.time_label = tk.Label(progress_frame, text=f"{self.t['time_elapsed']}00:00:00", font=("Consolas", 11, "bold"), fg="#555555")
        self.time_label.pack(side=tk.RIGHT)

        tk.Label(self.root, text=self.t["log_lbl"], font=self.font_title).pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(self.root, font=("Consolas", 9), bg="#1E1E1E", fg="#00FF00")
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def browse_source(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            norm_path = os.path.normpath(folder_selected)
            self.source_path.set(norm_path)
            if not self.output_path.get():
                self.output_path.set(f"{norm_path}_Results")

    def browse_output(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_path.set(os.path.normpath(folder_selected))

    def safe_print(self, text):
        def update_text():
            self.log_area.insert(tk.END, text)
            self.log_area.see(tk.END)
        self.root.after(0, update_text)

    def check_nvidia_gpu(self):
        try:
            subprocess.run(["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except:
            return False

    def check_docker_engine(self):
        try:
            subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            return True
        except:
            return False

    def start_docker_desktop(self):
        docker_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if os.path.exists(docker_path):
            try:
                subprocess.Popen([docker_path], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                return True
            except:
                return False
        return False

    # 🌟 核心新功能：自動解除 Windows WSL2 記憶體限制
    def optimize_wsl_memory(self):
        if os.name != 'nt':
            return False

        try:
            # 呼叫底層 API 取得這台電腦的實體記憶體大小
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

            total_ram_gb = stat.ullTotalPhys / (1024**3)
            
            # 分配 80% 的 RAM 給 Docker，最少 8GB
            target_ram = max(8, int(total_ram_gb * 0.8))
            target_swap = target_ram * 2

            wslconfig_path = os.path.join(os.path.expanduser("~"), ".wslconfig")
            config_content = f"[wsl2]\nmemory={target_ram}GB\nswap={target_swap}GB\n"

            # 檢查是否已經寫入過了
            if os.path.exists(wslconfig_path):
                with open(wslconfig_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "memory=" in content:
                        return False # 已經設定過，略過

            # 如果沒有設定過，自動寫入並重啟 WSL
            self.safe_print(self.t["log_wsl_fix"])
            with open(wslconfig_path, 'w', encoding='utf-8') as f:
                f.write(config_content)

            subprocess.run(["wsl", "--shutdown"], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.safe_print(self.t["log_wsl_done"])
            time.sleep(2)
            return True
        except Exception:
            return False

    def update_timer(self):
        if self.is_running and self.start_time:
            elapsed = int(time.time() - self.start_time)
            td = datetime.timedelta(seconds=elapsed)
            self.time_label.config(text=f"{self.t['time_elapsed']}{td}")
            self.root.after(1000, self.update_timer)

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
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.safe_print("="*60 + "\n")
        self.safe_print(f"📷 SOURCE: {source_dir}\n")
        self.safe_print(f"🎯 OUTPUT: {output_dir}\n")
        self.safe_print("="*60 + "\n")

        # 🌟 先執行智慧解封印
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

        odm_image = "opendronemap/odm:gpu" if has_gpu else "opendronemap/odm"
        command = ["docker", "run", "--rm"]
        
        if has_gpu:
            self.safe_print(self.t["log_gpu_yes"])
            command.extend(["--gpus", "all"])

        command.extend([
            "-v", f"{output_dir}:/datasets/project", 
            "-v", f"{source_dir}:/datasets/project/images:ro", 
            odm_image,  
            "--project-path", "/datasets", "project",
            "--dsm", 
            "--orthophoto-compression", "LZW",
            "--skip-report"
        ])

        if mode == "fast":
            command.extend(["--fast-orthophoto", "--max-concurrency", "14"])
        elif mode == "high":
            # 🌟 雙重保險：將高精度模式的同時運算核心壓至 2，避免記憶體峰值過高
            command.extend(["--pc-quality", "medium", "--dem-resolution", "5", "--max-concurrency", "2"])
        elif mode == "huge":
            command.extend([
                "--split", "80", 
                "--split-overlap", "15", 
                "--feature-quality", "lowest",
                "--min-num-features", "2000", 
                "--pc-quality", "lowest", 
                "--dem-resolution", "10", 
                "--max-concurrency", "2"
            ])

        self.safe_print(self.t["log_odm_start"])

        try:
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace', creationflags=creationflags
            )

            for line in process.stdout:
                self.safe_print(line)

            process.wait()

            if process.returncode == 0:
                self.safe_print("\n" + "="*60 + "\n")
                self.safe_print(self.t["log_clean_start"])
                time.sleep(2) 
                
                keep_list = ["odm_dem", "odm_orthophoto"]
                try:
                    for item in os.listdir(output_dir):
                        if item not in keep_list:
                            item_path = os.path.join(output_dir, item)
                            if os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                            else:
                                os.remove(item_path)
                    self.safe_print(self.t["log_clean_done"])
                except Exception:
                    pass

                self.safe_print(self.t["log_done"])
                self.safe_print("="*60 + "\n")
                
                final_time = self.time_label.cget('text').replace(self.t["time_elapsed"], "")
                msg = self.t["msg_done_body"].format(time=final_time, path=output_dir)
                messagebox.showinfo(self.t["msg_done_title"], msg)
            else:
                msg = self.t["msg_err_body"].format(code=process.returncode)
                messagebox.showerror(self.t["msg_err_title"], msg)

        except Exception as e:
            self.safe_print(f"\n❌ Exception: {e}\n")
        finally:
            self.reset_ui()

    def reset_ui(self):
        self.is_running = False
        self.progress_bar.stop() 
        def update_btn():
            self.btn_start.config(state=tk.NORMAL, text=self.t["btn_start"], bg="#4CAF50")
        self.root.after(0, update_btn)

if __name__ == "__main__":
    root = tk.Tk()
    app = DroneProcessingApp(root)
    root.mainloop()
