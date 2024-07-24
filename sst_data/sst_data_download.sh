for date in 20240620

do 
	#--- SST is only tracked once per day, so no time variable
    sst=https://www.ncei.noaa.gov/thredds/fileServer/OisstBase/NetCDF/V2.1/AVHRR/${date:0:6}/oisst-avhrr-v02r01."$date".nc
    sst_backup=https://www.ncei.noaa.gov/thredds/fileServer/OisstBase/NetCDF/V2.1/AVHRR/${date:0:6}/oisst-avhrr-v02r01."$date"_preliminary.nc
    
    wget --no-check-certificate -O sst_data/sst_$date $sst || wget -O sst_data/sst_$date $sst_backup
    echo "SST collected for "$date

done