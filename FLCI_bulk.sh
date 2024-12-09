#! /usr/bin/bash

#--- Make sure you're using flc_env on smiller2
for date in 20240401 20240402 20240403 20240404 20240405 20240406 20240407 20240408 20240409 20240410 20240411 20240412 20240413 20240414 20240415 20240416 20240417 20240418 20240419 20240420 20240421 20240422 20240423 20240424 20240425 20240426 20240427 20240428 20240429 20240430

#--- loop through the dates
do 

    #--- Collect model data: 
	#------ must be 00z, 06z, 12z, 18z
	dtime=06z
    wget -O model_data/gfs_$date https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs."$date"/${dtime:0:2}/atmos/gfs.t"$dtime".pgrb2.0p25.f000
    echo "GFS collected for "$date

    #--- Collect SST data:
    #------ SST is only tracked once per day, so no time variable
    sst=https://www.ncei.noaa.gov/thredds/fileServer/OisstBase/NetCDF/V2.1/AVHRR/${date:0:6}/oisst-avhrr-v02r01."$date".nc
    sst_backup=https://www.ncei.noaa.gov/thredds/fileServer/OisstBase/NetCDF/V2.1/AVHRR/${date:0:6}/oisst-avhrr-v02r01."$date"_preliminary.nc
    wget --no-check-certificate -O sst_data/sst_$date $sst || wget -O sst_data/sst_$date $sst_backup
    echo "SST collected for "$date

    #--- Run the FLC simulation for date
    #------ Image saved in composite/images/region and netCDF saved in composite/region
    python FLCI.py $date
    echo "FLC simulation run for "$date

    #--- Remove the GFS and SST data collected (do this manually, for safety)

done