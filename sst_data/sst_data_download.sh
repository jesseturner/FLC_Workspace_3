for date in 20240701 20240702 20240703 20240704 20240705 20240706 20240707 20240708 20240709 20240710 20240711 20240712 20240713 20240714 20240715

do 
	#--- SST is only tracked once per day, so no time variable
    sst=https://www.ncei.noaa.gov/thredds/fileServer/OisstBase/NetCDF/V2.1/AVHRR/${date:0:6}/oisst-avhrr-v02r01."$date".nc
    sst_backup=https://www.ncei.noaa.gov/thredds/fileServer/OisstBase/NetCDF/V2.1/AVHRR/${date:0:6}/oisst-avhrr-v02r01."$date"_preliminary.nc
    
    wget --no-check-certificate -O sst_data/sst_$date $sst || wget -O sst_data/sst_$date $sst_backup
    echo "SST collected for "$date

done