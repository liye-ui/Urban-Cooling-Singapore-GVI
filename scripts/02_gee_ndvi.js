// ==============================================================================
// Singapore 2023-2025 (June-August) Sentinel-2 10m NDVI Median Composite Script
// I, Li Ye, declare that Gemini 3.1 Pro was employed in July 2026 to write this script.
// ==============================================================================

// 1. Define the Region of Interest (ROI) for Singapore - covering the island's bounding box
var roi = ee.Geometry.Rectangle([103.6, 1.1, 104.1, 1.5]);

// 2. Sentinel-2 cloud masking function (based on QA60 band)
function maskS2clouds(image) {
  var qa = image.select('QA60');
  
  // Bit 10 represents Opaque clouds, Bit 11 represents Cirrus clouds
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  
  // When both bits are 0, it indicates clear conditions without clouds
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
    .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
    
  return image.updateMask(mask);
}

// 3. Load Sentinel-2 Surface Reflectance image collection and apply spatio-temporal filtering
print("Processing Sentinel-2 images for Singapore from June-August, 2023-2025...");
var s2_collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(roi)
  .filter(ee.Filter.calendarRange(2023, 2025, 'year'))  // Strictly filter by years
  .filter(ee.Filter.calendarRange(6, 8, 'month'))       // Strictly filter by months (June-August)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))  // Pre-filter images with more than 20% cloud cover to speed up computation
  .map(maskS2clouds);                                   // Apply precise pixel-level cloud masking

// 4. Calculate Median Composite
var s2_median = s2_collection.median();

// 5. Calculate NDVI (Normalized Difference Vegetation Index)
// Sentinel-2 Near-Infrared (NIR) is Band 8, Red is Band 4
var ndvi = s2_median.normalizedDifference(['B8', 'B4']).rename('NDVI');

// Clip to the standard bounding box of Singapore
var ndvi_singapore = ndvi.clip(roi);

// 6. Interactive visualization settings
Map.setCenter(103.82, 1.35, 11);
Map.setOptions('SATELLITE');

// Classic NDVI vegetation visualization color palette (from brown to dark green)
var ndviVis = {
  min: -0.2, // Water bodies or dense built-up areas usually fall in this range
  max: 0.8,  // Dense tropical rainforests or park canopies
  palette: [
    'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901', 
    '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', 
    '012E01', '011D01', '011301'
  ]
};

Map.addLayer(ndvi_singapore, ndviVis, 'Singapore NDVI 2023-2025 Median (10m)');

// 7. Submit export task to Google Drive
Export.image.toDrive({
  image: ndvi_singapore,
  description: 'Singapore_NDVI_Median_2023_2025_10m',
  folder: 'GEE_NDVI_Export',        // Google Drive folder name
  scale: 10,                        // Maintain the native 10-meter resolution
  region: roi,
  maxPixels: 1e13
});

print("✅ Script execution completed! Please click the 'Run' button in the 'Tasks' panel on the right to download the TIFF image.");
