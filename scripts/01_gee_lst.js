// ==============================================================================
// Singapore 2023-2025 (June-August) Landsat 8 LST Median Composite Script
// I, Li Ye, declare that Gemini 3.1 Pro was employed in July 2026 to write this script.
// ==============================================================================

// 1. Define the Region of Interest (ROI) for Singapore - covering the island's bounding box
var roi = ee.Geometry.Rectangle([103.6, 1.1, 104.1, 1.5]);

// 2. Landsat 8 Level-2 precise cloud masking function (masks both clouds and cloud shadows)
function mask_landsat_clouds(image) {
  var qa = image.select('QA_PIXEL');
  
  // Bit 3 represents Cloud, Bit 4 represents Cloud Shadow
  var cloudShadowBitMask = 1 << 4;
  var cloudsBitMask = 1 << 3;
  
  // When both bits are 0, it indicates clear conditions without interference
  var qa_cloud_shadow = qa.bitwiseAnd(cloudShadowBitMask).eq(0);
  var qa_cloud = qa.bitwiseAnd(cloudsBitMask).eq(0);
  
  // Combine masks and update the image mask
  var valid_mask = qa_cloud_shadow.and(qa_cloud);
  return image.updateMask(valid_mask);
}

// 3. Load Landsat 8 image collection and apply spatio-temporal filtering
print("Processing images for Singapore from June-August, 2023-2025...");
var landsat_collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterBounds(roi)
  .filter(ee.Filter.calendarRange(2023, 2025, 'year'))  // Strictly filter by years
  .filter(ee.Filter.calendarRange(6, 8, 'month'))       // Strictly filter by months (June, July, August)
  .map(mask_landsat_clouds);                            // Apply cloud masking

// 4. Calculate Median Composite and extract the Land Surface Temperature band
var lst_thermal_median = landsat_collection.select('ST_B10').median();

// 5. Core physical conversion: Convert raw DN values to Celsius (°C)
// Formula: LST_Celsius = (DN * 0.00341802 + 149.0) - 273.15
var lst_celsius = lst_thermal_median
  .multiply(0.00341802)
  .add(149.0)
  .subtract(273.15)
  .rename('LST_Celsius');

// Clip to the standard bounding box of Singapore
var lst_singapore = lst_celsius.clip(roi);

// 6. Interactive visualization settings
Map.setCenter(103.82, 1.35, 11);
Map.setOptions('SATELLITE');

var vis_params = {
  min: 22,
  max: 45,
  palette: ['blue', 'cyan', 'green', 'yellow', 'red']
};

Map.addLayer(lst_singapore, vis_params, 'Singapore LST 2023-2025 Median (C)');

// 7. Submit export task to Google Drive
Export.image.toDrive({
  image: lst_singapore,
  description: 'Singapore_LST_Median_2023_2025_30m',
  folder: 'GEE_LST_Export',         // Google Drive folder name
  scale: 30,                        // Maintain the native 30-meter resolution for spatial alignment
  region: roi,
  region: roi,
  maxPixels: 1e13
});

print("✅ Script execution completed! Please click the 'Run' button in the 'Tasks' panel on the right to download the TIFF image.");
