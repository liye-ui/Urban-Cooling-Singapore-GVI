# Run street scene semantic recognition to calculate GVI and point cleaning
# This script can be run in google colab
# I, Li Ye, declare that Gemini 3.1 Pro was employed in July 2026 to write this script.

import pandas as pd
import numpy as np
import os
import torch
from torch import nn
from PIL import Image
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation

from google.colab import drive
drive.mount('/content/drive')

# 1. Path and Parameter Configuration
# ==========================================
CSV_PATH = '/content/drive/MyDrive/High_Points.csv'        # Path to input sample points CSV
OUTPUT_CSV = '/content/drive/MyDrive/High_points_GVI.csv'   # Path to output CSV with GVI results
IMG_DIR = '/content/drive/MyDrive/GSV_Images_SG/High'       # Directory containing GSV images

HEADINGS = [0, 90, 180, 270]
OCCLUSION_THRESHOLD = 0.40  # Vehicle occlusion threshold: > 40% returns Null/None

# 2. Model Initialization (SegFormer)
# ==========================================
print("Loading SegFormer model...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device in use: {device}")

# Load feature extractor/processor and pre-trained model
processor = SegformerImageProcessor.from_pretrained("nvidia/segformer-b0-finetuned-cityscapes-512-1024")
model = SegformerForSemanticSegmentation.from_pretrained("nvidia/segformer-b0-finetuned-cityscapes-512-1024")
model.to(device)
model.eval()  # Set model to evaluation mode

# ==========================================
# 3. Core Processing Function
# ==========================================
def process_image(image_path):
    """
    Performs semantic segmentation on a single image, evaluates occlusion rate,
    and returns valid GVI value or None.
    """
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        return None # Unreadable images treated directly as Null

    # Feed image to Transformer
    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    # Upsample model logits back to original image resolution (640x640)
    upsampled_logits = nn.functional.interpolate(
        logits,
        size=image.size[::-1],
        mode="bilinear",
        align_corners=False,
    )

    # Get class ID with maximum probability per pixel
    pred_mask = upsampled_logits.argmax(dim=1)[0].cpu().numpy()
    total_pixels = pred_mask.size

    # Cityscapes Class Definitions:
    # Vehicle occlusion classes: 13 (car), 14 (truck), 15 (bus), 16 (train)
    # Greenery vegetation classes: 8 (vegetation), 9 (terrain)

    occlusion_mask = np.isin(pred_mask, [13, 14, 15, 16])
    occlusion_rate = occlusion_mask.sum() / total_pixels

   # 1. Vehicle Occlusion Evaluation
    if occlusion_rate > OCCLUSION_THRESHOLD:
        return None  # Severe occlusion, return Null

    # 2. Green View Index Calculation
    green_mask = np.isin(pred_mask, [8, 9])
    green_rate = green_mask.sum() / total_pixels

    return green_rate

# ==========================================
# 4. Iterate Over Sample Points and Update CSV
# ==========================================
df = pd.read_csv(CSV_PATH)
df['GVI_Mean'] = np.nan  # Initialize GVI column with NaN

print(f"\nStarting processing for {len(df)} sample points...")
discarded_points = []
processed_count = 0

for index, row in df.iterrows():
    point_id = int(row['ID'])
    valid_gvis = []
    null_count = 0

    for heading in HEADINGS:
        filename = f"{point_id}_{heading}.jpg"
        filepath = os.path.join(IMG_DIR, filename)

       # 1. File does not exist (removed during pre-screening or failed download)
        if not os.path.exists(filepath):
            null_count += 1
            continue

        # 2. File exists: run deep learning semantic segmentation
        gvi_val = process_image(filepath)

        if gvi_val is None:
            null_count += 1
        else:
            valid_gvis.append(gvi_val)

    # --------------------------------------
    # Point-Level Selection Logic:
    # "2 or more invalid directions out of 4" -> null_count >= 2
    # Requires at least 3 valid directional images to compute mean GVI
    # --------------------------------------
    if null_count >= 2:
        print(f"[Discarded] Sample Point ID: {point_id} dropped (Invalid directions: {null_count}/4)")
        discarded_points.append(point_id)
        # Maintained as NaN in DataFrame
    else:
        # Valid point: calculate mean GVI and write to DataFrame
        df.at[index, 'GVI_Mean'] = np.mean(valid_gvis)

    processed_count += 1
    if processed_count % 50 == 0:
        print(f"Inference completed for {processed_count} sample points...")

# ==========================================
# 5. Export Results
# ==========================================
df.to_csv(OUTPUT_CSV, index=False)


print("\n" + "="*40)
print("Geo-AI semantic segmentation and GVI calculation completed!")
print(f"Total invalid sample points discarded: {len(discarded_points)}")
print(f"Dataset with final mean GVI values saved to: {OUTPUT_CSV}")
print("="*40)
