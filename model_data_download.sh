#! /usr/bin/bash

for date in 20230920

do 

	dtime=06z

	wget https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs."$date"/${dtime:0:2}/atmos/gfs.t"$dtime".pgrb2.0p25.f000 -P model_data
    echo "GFS collected for "$date

done