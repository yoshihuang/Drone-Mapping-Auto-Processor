# Drone Mapping Auto-Processor (with GCP)
1. Introduction
This tool is a "One-Click Photogrammetry Solution" designed specifically for Unmanned Aerial Vehicle (UAV) imagery. You don't need to learn complex GIS software. Simply select the folder containing your drone photos, and the system will automatically handle all the heavy lifting in the background, now with full Ground Control Point (GCP) support.
🔥 Ultimate Features:
●	Interactive Visual Map: Built-in dynamic map that automatically plots photo GPS locations. Features LOD zooming for filenames, and uses "Red/Green" dots and "Black Triangles" to track processing status and GCP locations in real-time.
●	Survey-Grade GCP Support: Import standard WebODM GCP files. Built-in smart coordinate transformation engine (PyProj) automatically converts and displays various projection systems (e.g., UTM, TWD97) while executing centimeter-level geometric corrections.
●	Flawless Agricultural Merging Algorithm: Exclusive "Huge Dataset" parameters tuned specifically for highly homogeneous terrains (like massive farmlands) to completely eliminate patchwork islands and 3D stitching crashes.
●	GPU Acceleration & Auto-Cleanup: Auto-detects NVIDIA GPUs to engage the CUDA engine, and automatically deletes tens of gigabytes of temporary files after completion, leaving only the pure final output.
2. System & Hardware Requirements
●	OS: Windows 10 or Windows 11 (64-bit).
●	RAM: Minimum 16GB. If processing over 500 images, you MUST select the "Huge Dataset" mode. 32GB+ is highly recommended for the best experience.
●	GPU: NVIDIA Dedicated Graphics Card is highly recommended.
●	⚠️ CRITICAL: Your NVIDIA Graphics Driver MUST be updated to the latest version; otherwise, the GPU engine will fail to start.
●	Storage: At least 50GB of free space on a fast SSD.
3. Essential First-Time Setup
This application features an "Auto-Install Python Packages" function. You only need to ensure the following two core environments are installed before your first run:
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
4. Operation Guide: 3 Steps to Auto-Processing
Launch run_uav_GCP2.py. The system will automatically download necessary UI packages and start:
Step 1: Set Folders & Data
1.	Source Photos: Click "Browse..." and select the folder with your raw drone images. The map will instantly plot all photo locations with "Green Dots".
2.	Output Folder: The system will auto-fill this, or you can change it manually.
3.	Enable GCP: Check this box and load your .txt file if you have precision control points.
○	Note: Click "📝 Format Guide" to download a standard template, or "💡 How to Generate GCP" for software marking tutorials.
○	Successfully loaded GCPs will appear as "Black Triangles" on the map.
Step 2: Choose Processing Mode
●	⚡ Fast Orthophoto: Extremely fast. Skips dense 3D point clouds. Perfect for general crop inspections.
●	🏗️ High Precision: Generates highly detailed DSM and 3D terrain. Recommended for under 300 photos.
●	🗺️ Huge Dataset: Designed for massive projects (500+ photos). Uses the ultimate seamless merging algorithm to prevent OOM crashes.
Step 3: Start Auto Processing
1.	Click the green "🚀 Start Auto Processing" button.
2.	The system will optimize WSL memory, wake up Docker, and begin.
3.	Monitor the progress on the map: photos currently being processed will switch from "Green" to "Red".
4.	When you see the "✅ Processing and cleanup successful!" popup, open your output folder to find your final odm_orthophoto.tif and odm_dem.tif!
5. FAQ
●	Q1: The program closes immediately after double-clicking?
○	A: You likely forgot to check "Add to PATH" when installing Python. Please reinstall and ensure it's checked.
●	Q2: The system is stuck at "Waiting for Docker to warm up..."?
○	A: Open Docker Desktop manually from the Windows menu. If it's frozen, open Command Prompt (CMD), type wsl --shutdown, press Enter, and restart Docker.
●	Q3: Processing crashes with "Error Code: 137 or Killed"?
○	A: This is an Out-Of-Memory (OOM) error. Please switch to the "🗺️ Huge Dataset" mode and try again.
●	Q4: How do I view the output .tif files?
○	A: These are professional geo-referenced image files. Please use free open-source GIS software like QGIS, or commercial tools like AutoCAD Civil 3D to view and measure them.
