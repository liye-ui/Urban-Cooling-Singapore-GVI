# Getting google street images using Google Street View Static API
# This script can be run in google colab
# I, Li Ye, declare that Gemini 3.1 Pro was employed in July 2026 to write this script.

from google.colab import drive
import pandas as pd
import requests
import os
import time

# Mount Google Drive to the Colab environment
drive.mount('/content/drive')

# 1. Configure Google Drive paths and parameters
# ==========================================
CSV_PATH = '/content/drive/MyDrive/xxx.csv'

# Output directory for saving downloaded street view images
OUTPUT_DIR = '/content/drive/MyDrive/GSV_Images_SG/Low'

API_KEY = YOUR_API_KEY_HERE       # Replace with your actual key in local execution

# Street View image parameters
IMG_SIZE = '640x640'  # Resolution set to maximum clarity
PITCH = '0'           # Pitch angle set to 0 (eye-level)
HEADINGS = [0, 90, 180, 270]  # Four cardinal directions (North, East, South, West)

# Create the output directory if it does not exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created directory in Google Drive: {OUTPUT_DIR}")
# ==========================================
# 2. Read CSV data and download images to Google Drive
# ==========================================
df = pd.read_csv(CSV_PATH)
print(f"Total points loaded: {len(df)}. Estimated image downloads: {len(df) * 4}.")

success_count = 0
fail_count = 0

# Iterate over sample points
for index, row in df.iterrows():
    # 假设你的 CSV 里 ID 列叫 'ID'，经度叫 'lon'，纬度叫 'lat'
    point_id = int(row['ID'])
    lat = row['lat']
    lon = row['lon']

    for heading in HEADINGS:
        # Naming convention: ID_heading.jpg (e.g., 1_90.jpg)
        filename = f"{point_id}_{heading}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Skip downloading if the file already exists
        if os.path.exists(filepath):
            continue

        url = (f"https://maps.googleapis.com/maps/api/streetview?"
               f"size={IMG_SIZE}&location={lat},{lon}&heading={heading}"
               f"&pitch={PITCH}&key={API_KEY}")

        try:
            # Send HTTP GET request with a 10-second timeout
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                # Save binary image content directly to Google Drive
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                success_count += 1
            else:
                print(f"Download failed: Point {point_id}, Heading {heading}, Status code: {response.status_code}")
                fail_count += 1

        except Exception as e:
            print(f"Request exception: Point {point_id}, Error: {e}")
            fail_count += 1

        # Pause briefly to comply with API rate limits
        time.sleep(0.1)

    # Progress tracking
    if (index + 1) % 50 == 0:
        print(f"Progress: Processed {index + 1} points (all 4 directions).")

print(f"Task completed! Successful downloads: {success_count}, Failures: {fail_count}.")
