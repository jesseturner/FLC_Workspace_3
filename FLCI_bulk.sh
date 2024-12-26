#! /usr/bin/bash

#--- Make sure you're using flc_env on smiller2
for date in 20240921 20240922 20240923 20241101 20241102 20241103 20241104 20241105 20241106 20241107 20241108 20241109 20241110 20241111 20241112 20241113 20241114 20241115 20241116 20241117 20241118 20241119 20241120 20241121 20241122 20241123 20241124 20241125 20241126 20241127 20241128 20241129 20241130 #20241131


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