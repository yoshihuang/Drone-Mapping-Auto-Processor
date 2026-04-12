# Drone-Mapping-Auto-Processor
This tool is a "One-Click Photogrammetry Solution" designed specifically for Unmanned Aerial  Vehicle (UAV) imagery. You don't need to learn complex GIS software. Simply select the folder  containing your drone photos, and the system will automatically handle all the heavy lifting in  the background.
🚁 Drone Mapping Auto-Processor (Pro Ultimate) - User & Installation Manual

#Introduction
This tool is a "One-Click Photogrammetry Solution" designed specifically for Unmanned Aerial Vehicle (UAV) imagery. You don't need to learn complex GIS software. Simply select the folder containing your drone photos, and the system will automatically handle all the heavy lifting in the background.
🔥 Ultimate Features:
●	Smart i18n: Automatically detects your Windows OS language and switches between English and Chinese.
●	Dynamic GPU Acceleration: Automatically detects your NVIDIA GPU and seamlessly switches to the dedicated CUDA engine for massive speed boosts.
●	Auto-Cleanup Magic: Automatically deletes tens of gigabytes of temporary transition files once the task is complete, leaving you with only the pure final maps.

#System & Hardware Requirements
●	OS: Windows 10 or Windows 11 (64-bit).
●	RAM: Minimum 16GB. If processing over 500 images, you MUST select the "Huge Dataset" mode. 32GB+ is highly recommended for the best experience.
●	GPU: NVIDIA Dedicated Graphics Card is highly recommended.
○	⚠️ CRITICAL: Your NVIDIA Graphics Driver MUST be updated to the latest version (supporting CUDA 12.9 or higher); otherwise, the GPU engine will fail to start.
●	Storage: At least 50GB of free space on a fast SSD (NVMe preferred).

#Essential First-Time Setup
This application relies on two core environments. You only need to install them once:
Step 1: Install Python
1.	Visit the official website: https://www.python.org/downloads/
2.	Click "Download Python 3.x.x".
3.	[CRITICAL STEP] When you open the installer, you MUST check the box at the very bottom that says "Add python.exe to PATH" before clicking Install.
4.	Click "Install Now".
Step 2: Install Docker Desktop
1.	Visit the official website: https://www.docker.com/products/docker-desktop/
2.	Click "Download for Windows" and install (keep all default settings).
3.	Restart your computer after the installation.
4.	Open "Docker Desktop" from your Windows Start menu. Accept the terms on your first launch, and wait until the status indicator in the bottom left turns Green (Engine running).

#Operation Guide: 3 Steps to Auto-Processing
Double-click run_uav_pro.py or run_uav_map3.py (with map interface) to launch the tool. It will automatically display in English if your system is non-Chinese.

Step 1: Set Folders

●	Source Photos Folder: Click "Browse..." and select the folder containing your raw drone images (.JPG or .TIF). Note: The system mounts this as Read-Only to protect your original files.

●	Output Folder: The system will auto-fill this based on your source folder.
Step 2: Choose Processing Mode

●	⚡ Fast Orthophoto: Extremely fast. Skips dense 3D point clouds and stitches a 2D map directly. Perfect for crop inspections.

●	🏗️ High Precision: Generates highly detailed Digital Surface Models (DSM) and 3D terrain. Heavy on memory. Recommended for under 300 photos.

●	🗺️ Huge Dataset: Designed for massive projects (500+ photos). Automatically splits the map into blocks to prevent out-of-memory (OOM) crashes, then merges them flawlessly.

Step 3: Start Auto Processing

●	Click the green "🚀 Start Auto Processing" button.

●	The system will automatically wake up Docker, download the GPU engine if needed (approx. 4GB on the first run only), and begin processing.

●	When you see the popup saying "✅ Processing and cleanup successful!", open your output folder to find your final odm_orthophoto.tif and odm_dem.tif files! Drag them into QGIS to view your results.
