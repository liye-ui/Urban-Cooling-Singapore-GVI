# GSV images cleaning
# This script can be run in google colab
# I, Li Ye, declare that Gemini 3.1 Pro was employed in July 2026 to write this script.

import os
import cv2
import numpy as np
import shutil

from google.colab import drive
drive.mount('/content/drive')

# ==========================================
# 1. Directory Path Configuration
# ==========================================
# Input directory containing raw GSV images
INPUT_DIR = '/content/drive/MyDrive/GSV_Images_SG/High'

# Output directory for corrupted, missing, or poor-quality images ("trash bin")
TRASH_DIR = '/content/drive/MyDrive/GSV_Images_SG/Trash_Bin'

# Automatically create the trash bin directory if it does not exist
if not os.path.exists(TRASH_DIR):
    os.makedirs(TRASH_DIR)
    print(f"Created trash directory: {TRASH_DIR}")

# ==========================================
# 2. Quality Control Parameters
# ==========================================
MIN_SIZE_KB = 10        # Filter out empty images: files < 10 KB are flagged as invalid/placeholder images
DARK_THRESHOLD = 30     # Filter out extremely dark images: mean brightness < 30 (out of 255) flags dark scenes

# ==========================================
# 3. Image Cleaning Logic
# ==========================================
# Retrieve all JPG images from the input folder
all_images = [f for f in os.listdir(INPUT_DIR) if f.endswith('.jpg')]
print(f"Starting pre-screening, found {len(all_images)} images...\n")

trash_count_size = 0
trash_count_dark = 0

for filename in all_images:
    filepath = os.path.join(INPUT_DIR, filename)

   # Parse sample point ID (based on naming rule pointId_heading.jpg)
    try:
        point_id = filename.split('_')[0]
    except Exception as e:
        print(f"Filename parsing exception: {filename}")
        continue

    is_trashed = False
    trash_reason = ""

    # --------------------------------------
    # Check A: File Size Validation (filters out empty/no-data API response images)
    # --------------------------------------
    file_size_kb = os.path.getsize(filepath) / 1024.0
    if file_size_kb < MIN_SIZE_KB:
        is_trashed = True
        trash_reason = f"File size too small ({file_size_kb:.1f} KB)"
        trash_count_size += 1

    # --------------------------------------
    # Check B: Image Brightness Validation (filters out dark environments like tunnels and underpasses)
    # --------------------------------------
    if not is_trashed: # If file size is valid, load image and check brightness to save compute
        # Read image using OpenCV (Note: OpenCV loads images in BGR format by default)
        img = cv2.imread(filepath)

        if img is None:
            is_trashed = True
            trash_reason = "Corrupted image, unable to read"
            trash_count_size += 1
        else:
            # Convert to grayscale to compute mean global brightness
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            mean_brightness = np.mean(gray)

            if mean_brightness < DARK_THRESHOLD:
                is_trashed = True
                trash_reason = f"Extremely dark environment (Mean Brightness: {mean_brightness:.1f})"
                trash_count_dark += 1

    # --------------------------------------
    # Execute File Interception: Move invalid files and log details
    # --------------------------------------
    if is_trashed:
        trash_filepath = os.path.join(TRASH_DIR, filename)
        shutil.move(filepath, trash_filepath)
        print(f"[Interception] Sample Point ID: {point_id} | Image: {filename} | Reason: {trash_reason}")

# ==========================================
# 4. Summary Output
# ==========================================
total_trashed = trash_count_size + trash_count_dark
print("\n" + "="*40)
print(f"Pre-screening completed!")
print(f"Total invalid images removed: {total_trashed}")
print(f"  - Removed due to [Missing GSV / File size too small]: {trash_count_size}")
print(f"  - Removed due to [Extremely dark environment / Tunnels]: {trash_count_dark}")
print("="*40)
