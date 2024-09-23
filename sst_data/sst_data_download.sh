for date in 20240716 20240717 20240718 20240719 20240720 20240721 20240722 20240723 20240724 20240725 20240726 20240727 20240728 20240729 20240730 20240731

do 
	#--- SST is only tracked once per day, so no time variable
    sst=https://www.ncei.noaa.gov/thredds/fileServer/OisstBase/NetCDF/V2.1/AVHRR/${date:0:6}/oisst-avhrr-v02r01."$date".nc
    sst_backup=https://www.ncei.noaa.gov/thredds/fileServer/OisstBase/NetCDF/V2.1/AVHRR/${date:0:6}/oisst-avhrr-v02r01."$date"_preliminary.nc
    
    wget --no-check-certificate -O sst_data/sst_$date $sst || wget -O sst_data/sst_$date $sst_backup
    echo "SST collected for "$date

done