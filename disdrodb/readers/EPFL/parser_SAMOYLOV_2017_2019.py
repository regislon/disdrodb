#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 13:00:07 2022

@author: kimbo
"""
# -----------------------------------------------------------------------------.
# Copyright (c) 2021-2022 DISDRODB developers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------.
import os
import click
import time
import logging
import xarray as xr
import numpy as np

# Directory 
from disdrodb.io import check_directories
from disdrodb.io import get_campaign_name
from disdrodb.io import create_directory_structure

# Metadata 
from disdrodb.metadata import read_metadata
from disdrodb.check_standards import check_sensor_name

# IO 
from disdrodb.io import get_L0_fpath
from disdrodb.io import get_L1_netcdf_fpath
from disdrodb.io import read_L0_data

# L0_processing
from disdrodb.check_standards import check_L0_column_names
from disdrodb.check_standards import check_L0_standards
from disdrodb.L0_proc import get_file_list
from disdrodb.L0_proc import read_L0_raw_file_list
from disdrodb.L0_proc import write_df_to_parquet

# L1_processing
from disdrodb.L1_proc import create_L1_dataset_from_L0
from disdrodb.L1_proc import write_L1_to_netcdf
from disdrodb.L1_proc import create_L1_summary_statistics

# Logger 
from disdrodb.logger import create_logger
from disdrodb.logger import close_logger


# -------------------------------------------------------------------------.
# CLIck Command Line Interface decorator
@click.command()  # options_metavar='<options>'
@click.argument('raw_dir', type=click.Path(exists=True), metavar='<raw_dir>')
@click.argument('processed_dir', metavar='<processed_dir>')
@click.option('-l0', '--l0_processing', type=bool, show_default=True, default=True, help="Perform L0 processing")
@click.option('-l1', '--l1_processing', type=bool, show_default=True, default=True, help="Perform L1 processing")
@click.option('-nc', '--write_netcdf', type=bool, show_default=True, default=True, help="Write L1 netCDF4")
@click.option('-f', '--force', type=bool, show_default=True, default=False, help="Force overwriting")
@click.option('-v', '--verbose', type=bool, show_default=True, default=False, help="Verbose")
@click.option('-d', '--debugging_mode', type=bool, show_default=True, default=False, help="Switch to debugging mode")
@click.option('-l', '--lazy', type=bool, show_default=True, default=True, help="Use dask if lazy=True")
def main(raw_dir,
         processed_dir,
         l0_processing=True,
         l1_processing=True,
         write_netcdf=True,
         force=False,
         verbose=False,
         debugging_mode=False,
         lazy=True,
         ):
    """Script to process raw data to L0 and L1. \f
    
    Parameters
    ----------
    raw_dir : str
        Directory path of raw file for a specific campaign.
        The path should end with <campaign_name>.
        Example raw_dir: '<...>/disdrodb/data/raw/<campaign_name>'.
        The directory must have the following structure:
        - /data/<station_id>/<raw_files>
        - /metadata/<station_id>.json 
        For each <station_id> there must be a corresponding JSON file
        in the metadata subfolder.
    processed_dir : str
        Desired directory path for the processed L0 and L1 products. 
        The path should end with <campaign_name> and match the end of raw_dir.
        Example: '<...>/disdrodb/data/processed/<campaign_name>'.
    l0_processing : bool
        Whether to launch processing to generate L0 Apache Parquet file(s) from raw data.
        The default is True.
    l1_processing : bool
        Whether to launch processing to generate L1 netCDF4 file(s) from source netCDF or L0 data. 
        The default is True.
    write_netcdf: bool 
        Whether to save L1 as netCDF4 archive
        Write_netcdf must be True.
    force : bool
        If True, overwrite existing data into destination directories. 
        If False, raise an error if there are already data into destination directories. 
        The default is False
    verbose : bool
        Whether to print detailed processing information into terminal. 
        The default is False.
    debugging_mode : bool
        If True, it reduces the amount of data to process.
        - For L0 processing, it processes just 3 raw data files.
        - For L1 processing, it takes a small subset of the Apache Parquet dataframe.
        The default is False.
    lazy : bool
        Whether to perform processing lazily with dask. 
        If lazy=True, it employed dask.array and dask.dataframe.
        If lazy=False, it employed pandas.DataFrame and numpy.array.
        The default is True.
    
    Additional information:
    - The campaign name must semantically match between:
       - The ends of raw_dir and processed_dir paths 
       - The attribute 'campaign' within the metadata JSON file. 
    - The campaign name are set to be UPPER CASE. 
       
    """
    ####----------------------------------------------------------------------.
    ###########################
    #### CUSTOMIZABLE CODE ####
    ###########################
    #### - Define raw data headers
    # Notes
    # - In all files, the datalogger voltage hasn't the delimeter,
    #   so need to be split to obtain datalogger_voltage and rainfall_rate_32bit
    
    column_names =  ['temp1',
                        'temp2',
                        'temp3',
                        'temp4',
                        'temp5',
                        'temp6',
                        'temp7',
                        'temp8',
                        'temp9',
                        'temp10',
                        'temp11',
                        'temp12',
                        'temp13',
                        'temp14',
                        'temp15',
                        'temp16',
                        'temp17',
                        'temp18',
                        'temp19',
                        'temp20',
                        'temp21',
                        'temp22',
                        'temp23']

    # - Check name validity
    check_L0_column_names(column_names)

    ##------------------------------------------------------------------------.
    #### - Define reader options

    reader_kwargs = {}
    # - Define delimiter
    reader_kwargs["delimiter"] = ";"

    # - Avoid first column to become df index !!!
    reader_kwargs["index_col"] = False

    # - Define behaviour when encountering bad lines
    reader_kwargs["on_bad_lines"] = "skip"

    # - Define parser engine
    #   - C engine is faster
    #   - Python engine is more feature-complete
    reader_kwargs["engine"] = "python"

    # - Define on-the-fly decompression of on-disk data
    #   - Available: gzip, bz2, zip
    reader_kwargs["compression"] = "infer"

    # - Strings to recognize as NA/NaN and replace with standard NA flags
    #   - Already included: ‘#N/A’, ‘#N/A N/A’, ‘#NA’, ‘-1.#IND’, ‘-1.#QNAN’,
    #                       ‘-NaN’, ‘-nan’, ‘1.#IND’, ‘1.#QNAN’, ‘<NA>’, ‘N/A’,
    #                       ‘NA’, ‘NULL’, ‘NaN’, ‘n/a’, ‘nan’, ‘null’
    reader_kwargs["na_values"] = [
        "na",
        "",
        "error",
        "NA",
        "Error in data reading! 0000.000",
    ]

    # - Define max size of dask dataframe chunks (if lazy=True)
    #   - If None: use a single block for each file
    #   - Otherwise: "<max_file_size>MB" by which to cut up larger files
    reader_kwargs["blocksize"] = None  # "50MB"

    # Cast all to string
    reader_kwargs["dtype"] = str

    # Different enconding for this campaign
    reader_kwargs["encoding"] = "latin-1"

    # Skip first row as columns names
    reader_kwargs["header"] = None

    ##------------------------------------------------------------------------.
    #### - Define facultative dataframe sanitizer function for L0 processing
    # - Enable to deal with bad raw data files
    # - Enable to standardize raw data files to L0 standards  (i.e. time to datetime)
    df_sanitizer_fun = None

    def df_sanitizer_fun(df, lazy=False):
        # Import dask or pandas 
        if lazy: 
            import dask.dataframe as dd
        else: 
            import pandas as dd
            
        column_names = ['time',
                        'latitude',
                        'longitude',
                        'weather_code_synop_4680',
                        'weather_code_synop_4677',
                        'reflectivity_32bit',
                        'mor_visibility',
                        'laser_amplitude',
                        'number_particles',
                        'sensor_temperature',
                        'sensor_heating_current',
                        'sensor_battery_voltage',
                        'datalogger_error',
                        'rainfall_amount_absolute_32bit',
                        'All_0',
                        'raw_drop_concentration',
                        'raw_drop_average_velocity',
                        'raw_drop_number',
                        ]

        column_names_2 =   ['id',
                            'latitude',
                            'longitude',
                            'time',
                            'all_nan',
                            'rainfall_rate_32bit',
                            'rainfall_accumulated_32bit',
                            'weather_code_synop_4680',
                            'weather_code_synop_4677',
                            'reflectivity_32bit',
                            'mor_visibility',
                            'laser_amplitude',
                            'number_particles',
                            'sensor_temperature',
                            'sensor_heating_current',
                            'sensor_battery_voltage',
                            'All_0',
                            'rainfall_amount_absolute_32bit',
                            'datalogger_error',
                            'raw_drop_concentration',
                            'raw_drop_average_velocity',
                            'raw_drop_number',
                            'End_line'
                            ]
        
        # - Drop all nan in latitude (define in reader_kwargs['na_values'])
        df = df[~df.iloc[:,1].isna()]
        if len(df.index) == 0:
            df.columns = ['latitude',
                            'longitude',
                            'time',
                            'rainfall_rate_32bit',
                            'rainfall_accumulated_32bit',
                            'weather_code_synop_4680',
                            'weather_code_synop_4677',
                            'reflectivity_32bit',
                            'mor_visibility',
                            'laser_amplitude',
                            'number_particles',
                            'sensor_temperature',
                            'sensor_heating_current',
                            'sensor_battery_voltage',
                            'rainfall_amount_absolute_32bit',
                            'raw_drop_concentration',
                            'raw_drop_average_velocity',
                            'raw_drop_number',
                            ]
            # df = df.iloc[:,:18]
            return df
        
        # - If first column is ID, than is a different format
        
        if lazy:
            flag = df.iloc[:,0].str.isnumeric().all().compute()
        else:
            flag = df.iloc[:,0].str.isnumeric().all()
        
        if flag:
            # - Rename columns
            df.columns = column_names_2
            # - Remove ok from rainfall_rate_32bit
            if lazy:
                df["rainfall_rate_32bit"] = df["rainfall_rate_32bit"].str.replace("OK,","")
            else:
                # df['rainfall_rate_32bit'] = df['rainfall_rate_32bit'].str.split(',').str[-1]
               # - Suppress SettingWithCopyWarning error (A value is trying to be set on a copy of a slice from a DataFrame)
               dd.options.mode.chained_assignment = None
               df['rainfall_rate_32bit'] = df['rainfall_rate_32bit'].str.split(',').str[-1]
            
            # - Drop useless columns
            col_to_drop = ["id", "all_nan", "All_0", 'datalogger_error', 'End_line']
            df = df.drop(columns=col_to_drop)
            
            # - Check latutide and longitute
            df = df.loc[df["latitude"].astype(str).str.len() < 11]
            df = df.loc[df["longitude"].astype(str).str.len() < 11]
            
            # - Convert time column to datetime 
            df['time'] = dd.to_datetime(df['time'], errors='coerce')
            df = df.dropna()
            if len(df.index) == 0:
                for col in col_to_drop:
                    column_names_2.remove(col)
                df.columns = column_names_2
                return df
            df['time'] = dd.to_datetime(df['time'], format='%d-%m-%Y %H:%M:%S')
            
        else:
            
            # - Drop excedeed columns
            df = df.iloc[:,:18]
            # - Rename columns
            df.columns = column_names
            # - Drop useless columns
            col_to_drop = ["All_0", 'datalogger_error']
            df = df.drop(columns=col_to_drop)
            # - Convert time column to datetime 
            df['time'] = dd.to_datetime(df['time'], errors='coerce')
            df = df.dropna()
            if len(df.index) == 0:
                for col in col_to_drop:
                    column_names.remove(col)
                df.columns = column_names
                return df
            df['time'] = dd.to_datetime(df['time'], format='%d/%m/%Y %H:%M:%S')

        # - Drop columns if nan
        col_to_drop_if_na = ['latitude','longitude','raw_drop_concentration','raw_drop_average_velocity','raw_drop_number']
        df = df.dropna(subset = col_to_drop_if_na)
        
        # - Drop invalid raw_drop_concentration, raw_drop_average_velocity and raw_drop_number
        df = df.loc[df["raw_drop_concentration"].astype(str).str.len() == 224]
        df = df.loc[df["raw_drop_average_velocity"].astype(str).str.len() == 224]
        df = df.loc[df["raw_drop_number"].astype(str).str.len() == 4096]
        
        df = df[df['raw_drop_number'].str.contains('0\x100') == False]
        
        # - Cast dataframe to dtypes
        from disdrodb.data_encodings import get_L0_dtype_standards
        dtype_dict = get_L0_dtype_standards(sensor_name=sensor_name)
        
        dtype_dict_not_object = {}
        for k, v in dtype_dict.items():
            if v != 'object':
                dtype_dict_not_object[k] =  v
        dtype_dict_not_object.pop('time')
                
        for column in df.columns:
            if column in dtype_dict_not_object:
                df[column] = dd.to_numeric(df[column], errors='coerce')
                invalid_rows_index = df.loc[df[column].isna()].index
                if lazy:
                    if invalid_rows_index.size.compute() != 0:
                        df = df.dropna(subset=[column])
                else:
                    if invalid_rows_index.size != 0:
                        df = df.dropna(subset=[column])
                        # df = df.drop(invalid_rows_index)
                df[column] = df[column].astype(dtype_dict[column])

        return df

    ##------------------------------------------------------------------------.
    #### - Define glob pattern to search data files in raw_dir/data/<station_id>
    raw_data_glob_pattern= "*.log*"

    ####----------------------------------------------------------------------.
    ####################
    #### FIXED CODE ####
    ####################
    # -------------------------------------------------------------------------.
    # Initial directory checks
    raw_dir, processed_dir = check_directories(raw_dir, processed_dir, force=force)

    # Retrieve campaign name
    campaign_name = get_campaign_name(raw_dir)

    # -------------------------------------------------------------------------.
    # Define logging settings
    create_logger(processed_dir, "parser_" + campaign_name)
    # Retrieve logger
    logger = logging.getLogger(campaign_name)
    logger.info("### Script started ###")

    # -------------------------------------------------------------------------.
    # Create directory structure
    create_directory_structure(raw_dir, processed_dir)

    # -------------------------------------------------------------------------.
    #### Loop over station_id directory and process the files
    list_stations_id = os.listdir(os.path.join(raw_dir, "data"))

    # station_id = list_stations_id[1]
    for station_id in list_stations_id:
        # ---------------------------------------------------------------------.
        logger.info(f" - Processing of station_id {station_id} has started")
        # ---------------------------------------------------------------------.
        # Retrieve metadata
        attrs = read_metadata(raw_dir=raw_dir, station_id=station_id)
		
        # Retrieve sensor name
        sensor_name = attrs['sensor_name']
        check_sensor_name(sensor_name)

        # ---------------------------------------------------------------------.
        #######################
        #### L0 processing ####
        #######################
        if l0_processing:
            # Start L0 processing
            t_i = time.time()
            msg = " - L0 processing of station_id {} has started.".format(station_id)
            if verbose:
                print(msg)
            logger.info(msg)

            # -----------------------------------------------------------------.
            #### - List files to process
            glob_pattern = os.path.join("data", station_id, raw_data_glob_pattern)
            file_list = get_file_list(
                raw_dir=raw_dir,
                glob_pattern=glob_pattern,
                verbose=verbose,
                debugging_mode=debugging_mode,
            )
            

            ##------------------------------------------------------.
            #### - Read all raw data files into a dataframe  
            df = read_L0_raw_file_list(file_list=file_list,
                                       column_names=column_names,
                                       reader_kwargs=reader_kwargs,
                                       df_sanitizer_fun=df_sanitizer_fun,
                                       lazy=lazy,
                                       sensor_name=sensor_name,
                                       verbose=verbose)

            ##------------------------------------------------------.
            #### - Write to Parquet
            fpath = get_L0_fpath(processed_dir, station_id)
            write_df_to_parquet(df=df, fpath=fpath, force=force, verbose=verbose)
            ##------------------------------------------------------.
            #### - Check L0 file respects the DISDRODB standards
            check_L0_standards(fpath=fpath, sensor_name=sensor_name, verbose=verbose)
            ##------------------------------------------------------.
            # End L0 processing
            t_f = time.time() - t_i
            msg = " - L0 processing of station_id {} ended in {:.2f}s".format(
                station_id, t_f
            )
            if verbose:
                print(msg)
            logger.info(msg)

            ##------------------------------------------------------.
            # Delete temp variables
            del df

        # ---------------------------------------------------------------------.
        #######################
        #### L1 processing ####
        #######################
        if l1_processing:
            # Start L1 processing
            t_i = time.time()
            msg = " - L1 processing of station_id {} has started.".format(station_id)
            if verbose:
                print(msg)
            logger.info(msg)
            ##----------------------------------------------------------------.
            #### - Read L0
            df = read_L0_data(
                processed_dir,
                station_id,
                lazy=lazy,
                verbose=verbose,
                debugging_mode=debugging_mode,
            )

            # -----------------------------------------------------------------.
            #### - Create xarray Dataset
            ds = create_L1_dataset_from_L0(
                df=df, attrs=attrs, lazy=lazy, verbose=verbose
            )

            # -----------------------------------------------------------------.
            #### - Write L1 dataset to netCDF4
            if write_netcdf:
                fpath = get_L1_netcdf_fpath(processed_dir, station_id)
                write_L1_to_netcdf(ds, fpath=fpath, sensor_name=sensor_name)

            # -----------------------------------------------------------------.
            #### - Compute L1 summary statics
            create_L1_summary_statistics(
                ds,
                processed_dir=processed_dir,
                station_id=station_id,
                sensor_name=sensor_name,
            )

            # -----------------------------------------------------------------.
            # End L1 processing
            t_f = time.time() - t_i
            msg = " - L1 processing of station_id {} ended in {:.2f}s".format(
                station_id, t_f
            )
            if verbose:
                print(msg)
                print(" --------------------------------------------------")
            logger.info(msg)

            # -----------------------------------------------------------------.
        # ---------------------------------------------------------------------.
    # -------------------------------------------------------------------------.
    if verbose:
        print(msg)
    logger.info("---")
    logger.info(msg)
    logger.info("---")

    msg = "### Script finish ###"
    print(msg)
    logger.info(msg)

    close_logger(logger)


if __name__ == "__main__":
    main()
