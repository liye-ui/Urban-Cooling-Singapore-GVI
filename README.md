# Urban-Cooling-Singapore-GVI
Code and dataset for evaluating the spatial heterogeneity of urban greenery's cooling effects in Singapore. This project compares top-down NDVI with pedestrian centric street view GVI, utilizing SegFormer semantic segmentation and Geographically Weighted Regression (GWR).  
The workflow of this project is as follows:  
<img width="2685" height="1141" alt="outline (1)" src="https://github.com/user-attachments/assets/711211ba-0231-40ea-ae22-978127bcfbda" />

## About data
The data folder in this repository contains part of the source data used in this project. Other data including OLS and GWR results can be obtained via the Google Drive or Baidu Cloud links below:  
Google Drive: https://drive.google.com/drive/folders/14ZqHsgVk1oHJPCkOrwFv-qHYBNcmmMBH?usp=sharing  
Baidu Cloud：to be update  

## About code
The scripts folder in this repository contains the codes that used in this project.  
- 01 and 02 can be run in the Google Earth Engine pantform to acquire LST and NDVI data  
- 03,04 and 05 can be run in google colab to get google street images, perform data cleaning and calculate GVI respectively.  
