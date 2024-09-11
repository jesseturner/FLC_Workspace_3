# This code looks at all the viirs imagery files in the data directory and plots as single band swaths or composites of swaths
# For swath, Will stitch together granules if they are within 8 min of eachother.
# For composite, will stitch together if within 200 min of eachother.
# If data/geol files are grouped together (like from class), code will plot all bands, but as individual granules (won't stitch together into swaths or composites)
# If wanting to plot granules together as swaths or composites, recommendation is to use separate data/geol files
# 03 November 2023 - Script created by Bill Line (NOAA/NESDIS)
# Version 2-2 is optimized to preserve system memory
# Version 2-3 fixes instances around dateline
import os
import h5py
import glob
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf
import numpy as np
import time
import xarray as xr
from matplotlib.colors import ListedColormap
from pyresample.geometry import SwathDefinition
from pyresample import kd_tree
import psutil
import gc

start_time = time.time()
start_s_time = time.time() 
fig = None
ax = None
prev_timestamp = "99999"
prev_time = None
prev_sat = "temp"
prev_band = "temp"
prev_day = "00000000"
latlon=0

############Define directories and other details##################################################
# If you want to adjust colormaps or data ranges, scroll to the bottom of the script and
# adjust cmap and vmin/vmax values for appropriate "if statement".
cmap_dir = "/Users/jesseturner/Desktop/hitran_api/bill_line_DNB/" # directory with your colormaps
data_dir = "/Users/jesseturner/Desktop/hitran_api/bill_line_DNB/DNB_data/" # directory where the data files reside for this case
image_dir = "/Users/jesseturner/Desktop/hitran_api/bill_line_DNB/" # directory where you want the images to go
# GEO and Data grouped (like from CLASS) or separate (like from local ot CLASS)
file_format = "grouped" # "grouped" or "separate"
# If using grouped files from CLASS with multiple bands, and you want to plot just a single band from the CLASS file, 
# specify that band here (M01, M15, I1, etc). Otherwise, set to X
set_band = "X"
# Do you want to plot individual swaths, or multi-swath composites? "swath" or "composite"
swathORcomposite = "swath" # "swath" or "composite"
# Colorbar = on or off
cb = "off"
#latlon gridlines and labels "on" or "off"
lines = "off" # "on" or "off"
#
border_color = 'black'
#For M-bands and NCC, set to around 1000 if zoomed out, up to 4000 if focusing on details (ice edge, fires, lights, cloud detail)
#For I-bands, set to around 1000 if zoomed out, up to 8000 if focusing in on details
# For equal detail, these numbers need to be slightly higher (up to 2x) for CLASS data, since CLASS groups several granules resulting in larger area for grid to cover
set_grid= 2000
# Keep around 100-500. Raise if creating large image that you want to be able to zoom in on details.
set_dpi = 200
# Geographic area of image: wlon, elon, slat, nlat: lon is neg for WH, pos for EH
extent = (-73, -57, 33, 46) #--- Georges Bank
#extent = (-99.2, -89.5, 34.2, 39.4) # wlon, elon, slat, nlat: lon is neg for WH, pos for EH
#extent = (-180, 180, 60, 90) # When plotting directly over the poles with North/SouthPolarStereo (-90 in SHEM; slat can vary)
#extent = (-123, -69, 24.3, 52.5) # conus
#extent = (-12, 37, 29.5, 60) # Europe
#extent = (-179.9, 179.9, -89.9, 89.9) # global
###Ignore this part###
center_long = (extent[0] + extent[1]) / 2 
central_lat = (extent[2] + extent[3]) / 2 
par1 = extent[2] + (extent[3] - extent[2]) / 3 
par2 = extent[2] + (extent[3] - extent[2]) / 1.5 
######################
# Projection of image
#proj = ccrs.Mercator(central_longitude=center_long)
#proj = ccrs.NorthPolarStereo(central_longitude=center_long) # adjust the central_long to rotate image if looking directly over Pole
#proj = ccrs.SouthPolarStereo(central_longitude=center_long)
proj = ccrs.LambertConformal(central_longitude=center_long, central_latitude=central_lat, standard_parallels=(abs(par1),abs(par2)))
#proj = ccrs.Robinson(central_longitude=center_long)
#proj = ccrs.PlateCarree(central_longitude=center_long)
#################Should not need to go below this point############################################
if swathORcomposite in ["swath"]:
    print("Plotting Swaths")
    time2plot = 8
elif swathORcomposite in ["composite"]:
    print("Plotting Composites")
    time2plot = 200
else:
    print("incorect input, plotting swaths by default")
    time2plot = 8   
##################################################
set_grid2=set_grid # Adjust resolution of x-axis
############################################# 
if not os.path.exists(image_dir):
    os.makedirs(image_dir)
# Import custom colormap(s)
#ir
rgb_text = np.loadtxt(f"{cmap_dir}/ir_colormap.txt")
rgb_array = rgb_text.astype(float)
ir_cmap = ListedColormap(rgb_array)
#vis
rgb_text2 = np.loadtxt(f"{cmap_dir}/vis_squareroot_colormap.txt")
rgb_array2 = rgb_text2.astype(float)
vis_cmap = ListedColormap(rgb_array2)

# Define the bands
bands_order = ["M14", "M15", "M08", "M05", "NCC", "M01", "M02", "M03", "M04", "M06", "M07", "M09", "M10", "M11", "M12", "M13", "M16", "I1B", "I2B", "I3B", "I4B", "I5B"]

# Get a list of all files in the directory
all_files = os.listdir(data_dir)

# Filter and sort files based on filename criteria
files_data = [file for file in all_files if (file.startswith("V") or file[6:7] == "V") and file.endswith(".h5")]

if file_format in "separate":
    print("You are plotting with separate GEO and DATA files")
# Sort by sat, band, date, time
    files_datas = sorted(files_data, key=lambda x: (x[6:9], bands_order.index(x[1:4]),x[15:19], x[21:25]))
    # Filter files based on filename criteria
    prefixes_to_check = ["GMGTO", "GIGTO", "GNCCO"]
    files_geog = [file for file in all_files if any(file.startswith(prefix) for prefix in prefixes_to_check) and file.endswith(".h5")]
    files_geogs = sorted(files_geog, key=lambda x: (x[6:9],x[15:19], x[21:25]))
    # Create a dictionary to store associations between the common 27:31 part and the geog file
    geog_dict = {}
    for geog_file in files_geogs:
      key = (os.path.basename(geog_file)[6:9], os.path.basename(geog_file)[15:19], os.path.basename(geog_file)[21:25], os.path.basename(geog_file)[1:2])
      geog_dict[key] = geog_file
else:
    print("You are plotting with grouped GEO and DATA files")
# Sort by sat, date, time
    files_datas = sorted(files_data, key=lambda x: (x[-72:-69], x[-63:-59], x[-57:-53]))
    # Filter files based on filename criteria
    prefixes_to_check = ["GMGTO", "GIGTO", "GNCCO"]
    files_geog = [file for file in all_files if any(file.startswith(prefix) for prefix in prefixes_to_check) and file.endswith(".h5")]
    files_geogs = sorted(files_geog, key=lambda x: (x[-72:-69], x[-63:-59], x[-57:-53]))
    # Create a dictionary to store associations between the common 27:31 part and the geog file
    geog_dict = {}
    for geog_file in files_geogs:
      key = (os.path.basename(geog_file)[-72:-69], os.path.basename(geog_file)[-63:-59], os.path.basename(geog_file)[-57:-53], os.path.basename(geog_file)[1:2])
      geog_dict[key] = geog_file

for data_file in files_datas:
  gc.collect()  # Trigger garbage collection
  start_g_time = time.time()
  # find the key components of the data file
  if file_format in "separate":
      key = (os.path.basename(data_file)[6:9], os.path.basename(data_file)[15:19], os.path.basename(data_file)[21:25], os.path.basename(data_file)[1:2])
  else:
      key = (os.path.basename(data_file)[-72:-69], os.path.basename(data_file)[-63:-59], os.path.basename(data_file)[-57:-53], os.path.basename(data_file)[1:2])
  # Match the key components in the data file with that from the geog dictionary so that we use correct geog file with this data file. 
  if key in geog_dict:
    geog_file = geog_dict[key]

    if file_format in "separate":    
      timestamp = data_file[21:25]  # Extract the timestamp from the file name
      timestamp2 = (int(timestamp[0:2]) * 60) + int(timestamp[2:4])
      prev_timestamp2 = (int(prev_timestamp[0:2]) * 60) + int(prev_timestamp[2:4])
      day = data_file[11:19]
      band = data_file[1:4]
      sat = data_file[6:9]    
      if sat in ["j01"]:
        sat2 = "N20"
      if sat in ["j02"]:
        sat2 = "N21"
      if sat in ["npp"]:
        sat2 = "NPP"
      if band[2:3] in ["B"]:
        band = band[0:2]
      band = [band]
    else:    
      timestamp = data_file[-57:-53]  # Extract the timestamp from the file name
      timestamp2 = (int(timestamp[0:2]) * 60) + int(timestamp[2:4])
      prev_timestamp2 = (int(prev_timestamp[0:2]) * 60) + int(prev_timestamp[2:4])
      day = data_file[-67:-59]
      sat = data_file[-72:-69]    
      if sat in ["j01"]:
        sat2 = "N20"
      if sat in ["j02"]:
        sat2 = "N21"
      if sat in ["npp"]:
        sat2 = "NPP"
      # Find the indices where 'V' appears in the filename
      v_indices = [i for i, letter in enumerate(data_file) if letter == 'V']
      band = []
      # Extract three-letter sequences after each 'V'
      for index in v_indices:
          if index + 3 < len(data_file):
              three_letters = data_file[index + 1:index + 4]
              if three_letters[-1] == 'B':
                  three_letters = three_letters[:2]
              band.append(three_letters)
    if set_band[0:1] == "M" or set_band[0:1] == "I":
        band = [set_band]
    else:
        pass
    for band in band:
      if prev_day == day:
        timediff1 = timestamp2 - prev_timestamp2
      elif prev_day == "99999": 
        pass
      else:
        if int(day[4:6]) - int(prev_day[4:6]) == 0: # checking if same month 
          print("day:", day, day[6:8], prev_day, prev_day[6:8])
          if int(day[6:8]) - int(prev_day[6:8]) == 1: # checking if jsut one day later
            timediff1 = (timestamp2 + 1440) - prev_timestamp2    
          else: # if more than 1 day later
            timediff1 = 9999
        elif int(day[4:6]) - int(prev_day[4:6]) == 1: # checking if next month
          if int(day[6:8]) == 1: # Checking if 1st of the month
            timediff1 = (timestamp2 + 1440) - prev_timestamp2  
          else: # if not the first of the month
            timediff1 = 9999         
        else: # if not the next month
           if int(day[4:6]) == 1 and int(day[6:8]) == 1 and int(prev_day[4:6]) == 12 and int(prev_day[6:8]) == 31: # checking if first of new year
             timediff1 = (timestamp2 + 1440) - prev_timestamp2                
           else:
             timediff1 = 9999
      if prev_time is None or timediff1 > time2plot or prev_sat != sat or prev_band != band: # if new swath, plot old swath, then create new plot
        # Plot the previous loaded data (1 or many granules) if the new timestamp spread is greater than 7min (new swath)
        if fig is not None:
            if cb in ["on"]:
                cbar = plt.colorbar(img, ax=ax, pad=0.035, shrink=0.5)
                cbar.set_label(cbarl)     
            ax.set_title(f"{prev_day} {prev_timestamp}Z {prev_sat2} VIIRS {prev_band}", fontsize=14)
            print(f"Plotting Image: {prev_day} {prev_timestamp}Z for {prev_sat2} band {prev_band}")
            plt.savefig(f"{image_dir}/{prev_day}-{prev_timestamp}Z_{prev_sat2}_{prev_band}.jpg", dpi=set_dpi, bbox_inches='tight')
            plt.close(fig)
            print("---Swath Time %s seconds ---" % (time.time() - start_s_time))  
            start_g_time = time.time()
            start_s_time = time.time() 

        #this chunk will create a new plot for the first file in the new sequence, but wont create figure for it until above
        # The timestamp in the figure will be the first in the sequence, while that in the filename will be the last
        fig = plt.figure(figsize=(16, 9))
        ax = fig.add_subplot(1, 1, 1, projection=proj)
        ax.set_extent(extent, ccrs.PlateCarree())
        ax.coastlines(linewidth=0.5, color=border_color)
        ax.add_feature(cf.BORDERS, linewidth=0.5, edgecolor=border_color)
        ax.add_feature(cf.STATES, linewidth=0.3, edgecolor=border_color)
        if lines in ["on"]:
            gridlines = ax.gridlines(draw_labels=True, linestyle='dotted', linewidth=0.3)
            gridlines.xlabel_style = {'size': 8}
            gridlines.ylabel_style = {'size': 8}

      with h5py.File(f"{data_dir}/{data_file}", 'r') as f:
        if band in ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09"]: 
            sband = band[0] + band[2:]
        else:
            sband = band

        if band in ["M12", "M13", "M14", "M15", "M16"]: 
            bt = f['All_Data'][f'VIIRS-{band}-MOD-EDR_All']['BrightnessTemperature'][()]
            if band in ["M12", "M14", "M15", "M16"]: 
                BrightnessFactors = f['All_Data'][f'VIIRS-{band}-MOD-EDR_All']['BrightnessFactors'][()]
        if band in ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11"]: 
            bt = f['All_Data'][f'VIIRS-{sband}-MOD-EDR_All']['Reflectance'][()]
            if band in ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11"]: 
                BrightnessFactors = f['All_Data'][f'VIIRS-{sband}-MOD-EDR_All']['ReflectanceFactors'][()]
        if band in ["I4", "I5"]:
            bt = f['All_Data'][f'VIIRS-{band}-IMG-EDR_All']['BrightnessTemperature'][()]
            if band in ["I4", "I5"]: 
                BrightnessFactors = f['All_Data'][f'VIIRS-{band}-IMG-EDR_All']['BrightnessFactors'][()]
        if band in ["I1", "I2", "I3"]:
            bt = f['All_Data'][f'VIIRS-{sband}-IMG-EDR_All']['Reflectance'][()]
            if band in ["I1", "I2", "I3"]: 
                BrightnessFactors = f['All_Data'][f'VIIRS-{sband}-IMG-EDR_All']['ReflectanceFactors'][()]
        if band in ["NCC"]:
            bt = f['All_Data'][f'VIIRS-{sband}-EDR_All']['Albedo'][()]
            if band in ["NCC"]: 
                BrightnessFactors = f['All_Data'][f'VIIRS-{sband}-EDR_All']['AlbedoFactors'][()]
      if band in ["I1", "I2", "I3", "I4", "I5"]:
        with h5py.File(f"{data_dir}/{geog_file}", 'r') as f:
            lat = f['All_Data']['VIIRS-IMG-GTM-EDR-GEO_All']['Latitude'][()]
            lon = f['All_Data']['VIIRS-IMG-GTM-EDR-GEO_All']['Longitude'][()]
      elif band in ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11", "M12", "M13", "M14", "M15", "M16"]:
        with h5py.File(f"{data_dir}/{geog_file}", 'r') as f:
            lat = f['All_Data']['VIIRS-MOD-GTM-EDR-GEO_All']['Latitude'][()]
            lon = f['All_Data']['VIIRS-MOD-GTM-EDR-GEO_All']['Longitude'][()]
      else:
        with h5py.File(f"{data_dir}/{geog_file}", 'r') as f:
            lat = f['All_Data']['VIIRS-NCC-EDR-GEO_All']['Latitude'][()]
            lon = f['All_Data']['VIIRS-NCC-EDR-GEO_All']['Longitude'][()]

      # Apply the BrightnessFactors to the BrightnessTemperature
      if band in ["I1", "I2", "I3", "I4", "I5", "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11", "M12", "M14", "M15", "M16", "NCC"]:
        bt = BrightnessFactors[0] * bt + BrightnessFactors[1]
      # Apply Mask
      if band in ["I4", "I5", "M12", "M13", "M14", "M15", "M16"]:
        mask = (bt > 100) & (bt <= 365)
      elif band in ["I1", "I2", "I3", "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11"]:
        mask = (bt > -0.05) & (bt <= 1.6)
      else:
        mask = (bt > -100) & (bt < 990) & (lon > -180)
        #print(timestamp2)
# uncomment below if you want to adjust location of stitch. Need to adjust "if statement" timestamp thresholds and lon values.
#        if timestamp2 < 400:
#          mask = (bt > 0) & (bt < 990) & (lon > -77)
#        if timestamp2 > 400:
#          mask = (bt > 0) & (bt < 990) & (lon < -76)       

      lat = lat[mask]
      lon = lon[mask]
      bt = bt[mask]

      if lon.min() < 0 and lon.max() > 0:

        # Filter data for positive longitude
        lon_pos = lon[lon > 0]
        lat_pos = lat[lon > 0]
        bt_pos = bt[lon > 0]

        # Filter data for negative longitude
        lon_neg = lon[lon < 0]
        lat_neg = lat[lon < 0]
        bt_neg = bt[lon < 0]

        # Processing for positive longitude
        granule_area_pos = SwathDefinition(lon_pos, lat_pos)
        lat1d_pos = np.linspace(lat_pos.min() - 5, lat_pos.max() + 5, set_grid * 2)
        lon1d_pos = np.linspace(lon_pos.min() - 5, lon_pos.max() + 5, set_grid2 * 2)
        lons_pos, lats_pos = np.meshgrid(lon1d_pos, lat1d_pos)
        plot_area_pos = SwathDefinition(lons_pos, lats_pos)
        result_pos = kd_tree.resample_nearest(granule_area_pos, bt_pos, plot_area_pos, radius_of_influence=1500, epsilon=0.5, fill_value=np.nan)
        plot_rads = xr.DataArray(result_pos, dims=('lat', 'lon'), coords={'lat': lat1d_pos, 'lon': lon1d_pos})

        # Processing for negative longitude
        granule_area_neg = SwathDefinition(lon_neg, lat_neg)
        lat1d_neg = np.linspace(lat_neg.min() - 5, lat_neg.max() + 5, set_grid * 2)
        lon1d_neg = np.linspace(lon_neg.min() - 5, lon_neg.max() + 5, set_grid2 * 2)
        lons_neg, lats_neg = np.meshgrid(lon1d_neg, lat1d_neg)
        plot_area_neg = SwathDefinition(lons_neg, lats_neg)
        result_neg = kd_tree.resample_nearest(granule_area_neg, bt_neg, plot_area_neg, radius_of_influence=1500, epsilon=0.5, fill_value=np.nan)
        plot_rads2 = xr.DataArray(result_neg, dims=('lat', 'lon'), coords={'lat': lat1d_neg, 'lon': lon1d_neg})
        latlon = 1
      else:
        print("Does not cross dateline", lon.min(), lon.max())
        # convert granule to grid
        granule_area = SwathDefinition(lon, lat)
        lat1d = np.linspace(lat.min()-5, lat.max()+5, set_grid*2)
        lon1d = np.linspace(lon.min()-5, lon.max()+5, set_grid2*2)
        lons, lats = np.meshgrid(lon1d, lat1d)
        plot_area = SwathDefinition(lons, lats)
        result = kd_tree.resample_nearest(granule_area, bt, plot_area, radius_of_influence=1500, epsilon=0.5, fill_value=np.nan)
        plot_rads = xr.DataArray(result, dims=('lat', 'lon'), coords={'lat':lat1d, 'lon':lon1d})
        latlon=0

    # Plot the granule using pcolormesh. Modify cmap, vmin, vmax as needed
      if band in ["I5", "M14", "M15", "M16"]:
        img = plot_rads.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap=ir_cmap, vmin=150, vmax=340, add_colorbar=False)
        if latlon==1:
          img2 = plot_rads2.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap=ir_cmap, vmin=150, vmax=340, add_colorbar=False)
        else:
          pass
        cbarl = "Brightness Temperature (K)"
      if band in ["I4", "M12", "M13"]:
        img = plot_rads.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap="gray_r", vmin=200, vmax=367, add_colorbar=False)
        if latlon==1:
          img2 = plot_rads2.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap="gray_r", vmin=200, vmax=367, add_colorbar=False)
        else:
          pass
        cbarl = "Brightness Temperature (K)"
      if band in ["I1", "I2", "I3", "M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10", "M11"]:
        img = plot_rads.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap="gray", vmin=0.00, vmax=1.2, add_colorbar=False)
        if latlon==1:
          img2 = plot_rads2.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap="gray", vmin=0.00, vmax=1.2, add_colorbar=False)
        else:
          pass
        cbarl = "Albedo"
      if band in ["NCC"]:
        img = plot_rads.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap=vis_cmap, vmin=0.03, vmax=3.0, add_colorbar=False)
        #img = plot_rads.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap=vis_cmap, vmin=0, vmax=2, add_colorbar=False)
        if latlon==1:
          img2 = plot_rads2.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap=vis_cmap, vmin=0.05, vmax=2.0, add_colorbar=False)
          #img2 = plot_rads2.plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), cmap=vis_cmap, vmin=0, vmax=2, add_colorbar=False)
        else:
          pass
        cbarl = "Albedo"
      #del plot_rads, lat, lon, bt, result, plot_area, lons, lats, lat1d, lon1d, granule_area
      print("---Granule Time: %.2f seconds for %s %sZ---" % (time.time() - start_g_time, day, timestamp))
      print("---Total Time %.2f seconds ---" % (time.time() - start_time))

      # Track Memory
      process = psutil.Process(os.getpid())  # Get the current process
      memory_info = process.memory_info()  # Get memory usage information
      print(f"Memory usage: {memory_info.rss / 1024 / 1024} MB")

      prev_timestamp = timestamp
      prev_sat = sat
      prev_sat2 = sat2
      prev_day = day
      prev_band = band
      prev_time="yes"
      #Plot every granule for checking
      #plt.savefig(f"{image_dir}/{prev_day}-{prev_timestamp}Z_{prev_sat2}_{prev_band}-test.jpg", dpi=set_dpi, bbox_inches='tight')
  else:
    # If no corresponding geog file is found, you can handle it as needed
    print("No geog file found for:", data_file)
# Creating final figure
if fig is not None:
  if cb in ["on"]:
    cbar = plt.colorbar(img, ax=ax, pad=0.035, shrink=0.5)
    cbar.set_label(cbarl)
  ax.set_title(f"{prev_day} {prev_timestamp}Z {prev_sat2} VIIRS {prev_band}", fontsize=14)
  print(f"Plotting Image: {prev_day} {prev_timestamp}Z for {prev_sat2} band {prev_band} ... Final Image")
  plt.savefig(f"{image_dir}/{prev_day}-{prev_timestamp}Z_{prev_sat2}_{prev_band}.jpg", dpi=set_dpi, bbox_inches='tight')
  plt.close(fig)

print("--- %s seconds ---" % (time.time() - start_time))
