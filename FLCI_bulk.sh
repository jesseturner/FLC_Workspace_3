#! /usr/bin/bash

#--- Make sure you're using flc_env on smiller2
for date in 20231202 20231203 20231204 20231205 20231206 20231207 20231208 20231209 20231210 20231211 20231212 20231213 20231214 20231215 20231216 20231217 20231218 20231219 20231220 20231221 20231222 20231223 20231224 20231225 20231226 20231227 20231228 20231229 20231230 20231231

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