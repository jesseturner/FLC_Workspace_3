#!/usr/bin/bash

#--- Make sure you're using flc_env on smiller2
for date in 20240301
do 
    #--- Collect model data: 
    #------ must be 00z, 06z, 12z, 18z
    dtime=06z
    model_url="https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.$date/${dtime:0:2}/atmos/gfs.t$dtime.pgrb2.0p25.f000"
    model_file="model_data/gfs_$date"

    # Check if the model file already exists locally
    if [[ -f "$model_file" ]]; then
        echo "GFS file already exists for $date, skipping download."
    else
        wget -O "$model_file" "$model_url"
        echo "GFS collected for $date"
    fi

    #--- Collect SST data:
    #------ SST is only tracked once per day, so no time variable
    sst_url="https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/${date:0:6}/oisst-avhrr-v02r01.$date.nc"
    sst_file="sst_data/sst_$date"

    # Check if the SST file already exists locally
    if [[ -f "$sst_file" ]]; then
        echo "SST file already exists for $date, skipping download."
    else
        wget --no-check-certificate -O "$sst_file" "$sst_url"
        echo "SST collected for $date"
    fi

    #--- Run the FLC simulation for date
    #------ Image saved in composite/images/region and netCDF saved in composite/region
    if [[ -f "$model_file" && -f "$sst_file" ]]; then
        python FLCI.py "$date"
        echo "FLC simulation run for $date"
    else
        echo "Skipping FLC simulation for $date due to missing input data."
    fi

    #--- Remove the GFS and SST data collected (do this manually, for safety)

done
