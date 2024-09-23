#! /usr/bin/bash

for date in 20240716 20240717 20240718 20240719 20240720 20240721 20240722 20240723 20240724 20240725 20240726 20240727 20240728 20240729 20240730 20240731

do 
	#--- must be 00z, 06z, 12z, 18z
	dtime=06z

	#--- data can be browsed at: https://noaa-gfs-bdp-pds.s3.amazonaws.com/index.html
	wget -O model_data/gfs_$date https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs."$date"/${dtime:0:2}/atmos/gfs.t"$dtime".pgrb2.0p25.f000
    echo "GFS collected for "$date

done