#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 15:49:23 2021

@author: kimbo
"""

import pandas as pd
import dask.dataframe as dd
import os
import xarray as xr
import netCDF4
from pprint import pprint



file_path = "/SharedVM/Campagne/DELFT/Processed/Wagenigen/L1/WAGENIGEN_s10.nc"

asd = ['/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141001.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141002.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141003.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141004.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141005.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141006.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141007.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141008.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141009.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141010.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141011.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141012.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141013.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141014.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141015.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141016.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141017.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141018.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141019.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141020.nc', '/SharedVM/Campagne/DELFT/Raw/WAGENIGEN/data/10/Disdrometer_20141021.nc']

ds = xr.open_dataset(file_path)

ds = xr.open_mfdataset(asd,engine='netcdf4', combine='nested', concat_dim='times')









































