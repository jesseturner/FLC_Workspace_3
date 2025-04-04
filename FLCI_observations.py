# FLCI Observations
# Using radiosonde for atmosphere, OISST for surface
# Single point estimation

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as feature

date_str = "20240620"
target_lat = 43.820069
target_lon = -66.164790 #113.83

#--- Values from radiosonde
#------ Entered manually for speed
if date_str == "20250312":
    pressure_levels = [1004, 1000, 996, 981, 973, 967.9, 967.0, 944.0, 932.7, 925, 903, 898.7, 894, 865.6, 864, 850]
    mix_ratio = [4.82, 4.64, 4.65, 4.76, 4.83, 4.69, 4.66, 5.47, 4.65, 4.15, 2.55, 2.7, 2.87, 2.21, 2.18, 1.98]
    temperatures = [3.4, 3.4, 3.4, 3.8, 7.8, 8.1, 8.2, 6.8, 6.3, 6.0, 5.2, 4.9, 4.6, 2.7, 2.6, 2.2]
if date_str == "20240620":
    pressure_levels = [1023, 1008, 10001, 1000, 999, 990, 988.4, 971.0, 954.4, 952, 925, 921.8, 890, 884, 859.1, 850]
    mix_ratio = [10.86, 10.74, 10.82, 11.19, 11.28, 12.38, 12.62, 15.50, 14.68, 14.56, 14.43, 14.35, 13.52, 13.36, 11.09, 10.33]
    temperatures = [17.4, 16.0, 16.4, 17.2, 18.4, 20.8, 20.9, 22.2, 23.6, 23.8, 22.4, 22.2, 20.5, 20.2, 19.2, 18.8]

#--- Region (Used for figure)
#--- Gulf Stream
# latitude_north = 51
# latitude_south = 30
# longitude_west = -80
# longitude_east = -55

#--- Georges Bank
latitude_north = 46
latitude_south = 33
longitude_west = -73
longitude_east = -57

sst_file = "sst_data/sst_"+date_str
sst_ds = xr.open_dataset(sst_file, engine='netcdf4')
sst_ds =  sst_ds.squeeze()

#--- Convert from C to K
sst_ds.sst.values = sst_ds.sst.values+273.15

#--- Select nearest point
nearest_valid = sst_ds.sst.sel(lat=target_lat, lon=target_lon+360, method="nearest")
lat = nearest_valid.lat.values
lon = nearest_valid.lon.values
sst = nearest_valid.values
print(f"Selected latitude: {lat}, Selected longitude: {lon-360}")
print(f"SST Value: {sst}")

#--- Put in kg/kg units
mix_ratio_kgkg = [x / 1000 for x in mix_ratio]

#--- Put in K units
temperatures_K = [x + 273.15 for x in temperatures]

#--- Create the mass density table
g = 9.807 #m s-2
optical_masses = []
for i in range(len(pressure_levels)-1):
    p1 = pressure_levels[i]*100 #kg s-2 m-1
    p2 = pressure_levels[i+1]*100 #kg s-2 m-1
    dp = p1-p2
    r_g = (mix_ratio_kgkg[i] + mix_ratio_kgkg[i+1]) / 2 #kg kg-1
    optical_masses.append((1/g)*r_g*dp) #kg m-2

#--- Open mass extinction look-up tables
mass_ext_df_13 = pd.read_pickle('tables/mass_ext_band13')
mass_ext_df_14 = pd.read_pickle('tables/mass_ext_band14')
mass_ext_df_07 = pd.read_pickle('tables/mass_ext_band07')

#--------- Pre-calculate nearest temperature and pressure indices for all bands
nearest_temp_indices_07 = np.argmin((mass_ext_df_07.index.values[:, None] - temperatures_K)**2, axis=0)
nearest_pressure_indices_07 = np.argmin((mass_ext_df_07.columns.values[:, None] - pressure_levels)**2, axis=0)

nearest_temp_indices_13 = np.argmin((mass_ext_df_13.index.values[:, None] - temperatures_K)**2, axis=0)
nearest_pressure_indices_13 = np.argmin((mass_ext_df_13.columns.values[:, None] - pressure_levels)**2, axis=0)

nearest_temp_indices_14 = np.argmin((mass_ext_df_14.index.values[:, None] - temperatures_K)**2, axis=0)
nearest_pressure_indices_14 = np.argmin((mass_ext_df_14.columns.values[:, None] - pressure_levels)**2, axis=0)

#--------- Pre-allocate arrays
optical_thickness_07 = np.zeros(len(pressure_levels))
optical_thickness_13 = np.zeros(len(pressure_levels))
optical_thickness_14 = np.zeros(len(pressure_levels))

for z in range(len(pressure_levels)-1):         
    optical_mass_value = optical_masses[z]

    # Lookup the mass extinction values using pre-calculated indices
    mass_ext_value_07 = mass_ext_df_07.iloc[nearest_temp_indices_07[z], nearest_pressure_indices_07[z]]
    optical_thickness_07[z] = optical_mass_value * mass_ext_value_07

    mass_ext_value_13 = mass_ext_df_13.iloc[nearest_temp_indices_13[z], nearest_pressure_indices_13[z]]
    optical_thickness_13[z] = optical_mass_value * mass_ext_value_13

    mass_ext_value_14 = mass_ext_df_14.iloc[nearest_temp_indices_14[z], nearest_pressure_indices_14[z]]
    optical_thickness_14[z] = optical_mass_value * mass_ext_value_14


#--- Function for blackbody radiance
def blackbody_radiance(T, wl):
    h = 6.626e-34
    c = 3e8
    k = 1.380e-23
    B = (2*h*c**2)/(wl**5 * (np.exp((h*c)/(k*wl*T))-1))
    return B

#--- Function for expected radiance from surface
def I_sfc(T_sfc, optical_thickness, wl):
    mu = 1
    tau_star = np.sum(optical_thickness, axis=0)
    I_sfc = blackbody_radiance(T_sfc, wl)*np.exp(-tau_star/mu)
    return I_sfc


#--- Function for expected radiance from atmosphere
def I_atm(optical_thickness, press_levels, temperatures, wl):
    p_len = np.shape(optical_thickness)[0] - 1
    I_levels = []
    mu = 1
    for i in range(p_len):
        T = np.array(temperatures[i])
        B = blackbody_radiance(T, wl)
        tau_above = np.sum(optical_thickness[i+1:], axis=0)
        tau_level = np.sum(optical_thickness[i:], axis=0)
        dp = press_levels[i+1] - press_levels[i]
        dT_dp = ((np.exp(-tau_above/mu)) - (np.exp(-tau_level/mu))) / dp
        I_level = B*dT_dp*dp
        I_levels.append(I_level)

    I_atm = np.sum(I_levels, axis=0)
    return I_atm


#--- Function for brightness temperature
def brightness_temperature(I, wl):
    h = 6.626e-34
    c = 3e8
    k = 1.380e-23
    Tb = (h*c)/(k*wl * np.log(1 + ((2*h*c**2)/(I*wl**5))))
    return Tb

#--- Setting wavelengths for BTD
first_wl = 11.2e-6
first_optical_thickness = optical_thickness_14
first_wl_str = str(first_wl*1e6).replace(".", "_")
second_wl = 3.9e-6
second_optical_thickness = optical_thickness_07
second_wl_str = str(second_wl*1e6).replace(".", "_")

#--- Calculate the results
first_I_tot = I_sfc(sst, first_optical_thickness, first_wl) + I_atm(first_optical_thickness, pressure_levels, temperatures_K, first_wl)
second_I_tot = I_sfc(sst, second_optical_thickness, second_wl) + I_atm(second_optical_thickness, pressure_levels, temperatures_K, second_wl)

BTD = brightness_temperature(first_I_tot, first_wl) - brightness_temperature(second_I_tot, second_wl)

formatted_T = ', '.join(f"{t:.2f}" for t in temperatures_K)
formatted_w = ', '.join(f"{w:.2e}" for w in mix_ratio_kgkg)
print(f"Temperatures: {formatted_T}")
print(f"Mixing Ratios (kg/kg): {formatted_w}")
print(f"BTD: {BTD:.4f}")

#--- Plot the result
projection=ccrs.PlateCarree(central_longitude=0)
fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})
from matplotlib.colors import LinearSegmentedColormap
colors = [(0, '#A9A9A9'), (0.5, 'white'), (1, '#1167b1')]  # +3 = blueish teal, 0 = white, -3 = grey
cmap = LinearSegmentedColormap.from_list('custom_cmap', colors)
c=ax.scatter(lon-360, lat, c=BTD, cmap=cmap, s=3000, edgecolor='black', linewidth=1, vmin=-3, vmax=3, zorder=5)
clb = plt.colorbar(c, shrink=0.4, pad=0.02, ax=ax, extend='both')
clb.set_ticks([-2.4, -1.6, -0.8, 0, 0.8, 1.6, 2.4])
clb.ax.tick_params(labelsize=15)
clb.set_label('(K)', fontsize=15)
ax.set_extent([longitude_west, longitude_east, latitude_south, latitude_north], crs=ccrs.PlateCarree())
ax.set_title("Estimated BTD (Cloud-Free)", fontsize=20, pad=10)
ax.coastlines(resolution='50m', color='black', linewidth=1)
ax.add_feature(feature.LAND, edgecolor='#000', facecolor='#000', zorder=10)
gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', linestyle='--', zorder=0)
gl.top_labels = False
gl.right_labels = False
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f'{x:.1f}°E' if x >= 0 else f'{-x:.1f}°W'))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, pos: f'{y:.1f}°N' if y >= 0 else f'{-y:.1f}°S'))
fig.savefig("flc_estimation_figure/"+date_str, dpi=200, bbox_inches='tight')