#! /usr/bin/bash

#--- Make sure you're using flc_env on smiller2
#for date in 20240801 20240802 20240803 20240804  
for date in 20240805 20240806 20240807 20240808 20240809 20240810 20240811 20240812 20240813 20240814 20240815 20240816 20240817 20240818 20240819 20240820 20240821 20240822 20240823 20240824 20240825 20240826 20240827 20240828 20240829 20240830 20240831

#--- loop through the dates
do 

    #--- Collect model data: 
	#------ must be 00z, 06z, 12z, 18z
	dtime=06z
    wget -O model_data/gfs_$date https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs."$date"/${dtime:0:2}/atmos/gfs.t"$dtime".pgrb2.0p25.f000
    echo "GFS collected for "$date

    #--- Collect SST data:
    #------ SST is only tracked once per day, so no time variable
    sst_path=https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/${date:0:6}/oisst-avhrr-v02r01."$date".nc
    wget --no-check-certificate -O sst_data/sst_$date $sst_path
    echo "SST collected for "$date

    #--- Run the FLC simulation for date
    #------ Image saved in composite/images/region and netCDF saved in composite/region
    python FLCI.py $date
    echo "FLC simulation run for "$date

    #--- Remove the GFS and SST data collected (do this manually, for safety)

done