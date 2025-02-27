#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 04:57:12 2022

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
    
    column_names_temp = ['temp']
    
    column_names = ['start_identifier',
                    'device_address',
                    'sensor_serial_number',
                    'date_sensor',
                    'time_sensor',
                    'weather_code_synop_4677_5min',
                    'weather_code_synop_4680_5min',
                    'weather_code_metar_4678_5min',
                    'precipitation_rate_5min',
                    'weather_code_synop_4677',
                    'weather_code_synop_4680',
                    'weather_code_metar_4678',
                    'precipitation_rate',
                    'rainfall_rate',
                    'snowfall_rate',
                    'precipitation_accumulated',
                    'mor_visibility',
                    'reflectivity',
                    'quality_index',
                    'max_hail_diameter',
                    'laser_status',
                    'static_signal',
                    'laser_temperature_analog_status',
                    'laser_temperature_digital_status',
                    'laser_current_analog_status',
                    'laser_current_digital_status',
                    'sensor_voltage_supply_status',
                    'current_heating_pane_transmitter_head_status',
                    'current_heating_pane_receiver_head_status',
                    'temperature_sensor_status',
                    'current_heating_voltage_supply_status',
                    'current_heating_house_status',
                    'current_heating_heads_status',
                    'current_heating_carriers_status',
                    'control_output_laser_power_status',
                    'reserve_status',
                    'temperature_interior',
                    'laser_temperature',
                    'laser_current_average',
                    'control_voltage',
                    'optical_control_voltage_output',
                    'sensor_voltage_supply',
                    'current_heating_pane_transmitter_head',
                    'current_heating_pane_receiver_head',
                    'temperature_ambient',
                    'current_heating_voltage_supply',
                    'current_heating_house',
                    'current_heating_heads',
                    'current_heating_carriers',
                    'number_particles',
                    'number_particles_internal_data',
                    'number_particles_min_speed',
                    'number_particles_min_speed_internal_data',
                    'number_particles_max_speed',
                    'number_particles_max_speed_internal_data',
                    'number_particles_min_diameter',
                    'number_particles_min_diameter_internal_data',
                    'number_particles_no_hydrometeor',
                    'number_particles_no_hydrometeor_internal_data',
                    'number_particles_unknown_classification',
                    'number_particles_unknown_classification_internal_data',
                    'number_particles_class_1',
                    'number_particles_class_1_internal_data',
                    'number_particles_class_2',
                    'number_particles_class_2_internal_data',
                    'number_particles_class_3',
                    'number_particles_class_3_internal_data',
                    'number_particles_class_4',
                    'number_particles_class_4_internal_data',
                    'number_particles_class_5',
                    'number_particles_class_5_internal_data',
                    'number_particles_class_6',
                    'number_particles_class_6_internal_data',
                    'number_particles_class_7',
                    'number_particles_class_7_internal_data',
                    'number_particles_class_8',
                    'number_particles_class_8_internal_data',
                    'number_particles_class_9',
                    'number_particles_class_9_internal_data',
                    'raw_drop_number',
                    ]
    
    # - Check name validity
    check_L0_column_names(column_names)

    ##------------------------------------------------------------------------.
    #### - Define reader options

    reader_kwargs = {}

    # - Define delimiter
    reader_kwargs['delimiter'] = '#'

    # - Avoid first column to become df index !!!
    reader_kwargs["index_col"] = False  

    # - Define behaviour when encountering bad lines 
    reader_kwargs["on_bad_lines"] = 'skip'

    # - Define parser engine 
    #   - C engine is faster
    #   - Python engine is more feature-complete
    reader_kwargs["engine"] = 'python'

    # - Define on-the-fly decompression of on-disk data
    #   - Available: gzip, bz2, zip 
    reader_kwargs['compression'] = 'infer'  

    # - Strings to recognize as NA/NaN and replace with standard NA flags 
    #   - Already included: ‘#N/A’, ‘#N/A N/A’, ‘#NA’, ‘-1.#IND’, ‘-1.#QNAN’, 
    #                       ‘-NaN’, ‘-nan’, ‘1.#IND’, ‘1.#QNAN’, ‘<NA>’, ‘N/A’, 
    #                       ‘NA’, ‘NULL’, ‘NaN’, ‘n/a’, ‘nan’, ‘null’
    reader_kwargs['na_values'] = ['na', '', 'error', 'NA', 'NP   ']

    # - Define max size of dask dataframe chunks (if lazy=True)
    #   - If None: use a single block for each file
    #   - Otherwise: "<max_file_size>MB" by which to cut up larger files
    reader_kwargs["blocksize"] = None # "50MB" 

    # Cast all to string
    reader_kwargs["dtype"] = str

    # Skip first row as columns names
    reader_kwargs['header'] = None

    # Skip first 3 rows
    reader_kwargs['skiprows'] = 3

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
            
        # Drop header's log rows
        df = df.loc[df['temp'].astype(str).str.len() > 30]

        # Split first 80 columns
        df = df['temp'].str.split(';', n=79, expand=True)
        
        df.columns = column_names

        # Clean raw_drop_number (ignore last 5 column)
        df['raw_drop_number'] = df['raw_drop_number'].str[:1760]
        
        # Drop row if start_identifier different than 00
        df = df.loc[df["start_identifier"].astype(str) == '00']
        
        # Merge time
        df['time'] = df['date_sensor'].astype(str) + ' ' + df['time_sensor']
        # Drop rows with invalid date
        df = df.loc[df["time"].astype(str).str.len() == 17]
        try:
            df['time'] = dd.to_datetime(df['time'], format='%d.%m.%y %H:%M:%S')
        except ValueError:
            df['time'] = dd.to_datetime(df['time'], format='%d.%m.%y %H:%M:%S', errors='coerce')
            df = df.loc[df.time.notnull()]
            
        # Drop invalid rows
        df = df.loc[df["raw_drop_number"].astype(str).str.len() == 1760]

        # Columns to drop
        columns_to_drop = ['start_identifier',
                        'device_address',
                        'sensor_serial_number',
                        'date_sensor',
                        'time_sensor',
                        'weather_code_synop_4677_5min',
                        'weather_code_synop_4680_5min',
                        'weather_code_metar_4678_5min',
                        'weather_code_metar_4678',
                        'quality_index',
                        'max_hail_diameter',
                        'laser_status',
                        'static_signal',
                        'laser_temperature_analog_status',
                        'laser_temperature_digital_status',
                        'laser_current_analog_status',
                        'laser_current_digital_status',
                        'sensor_voltage_supply_status',
                        'current_heating_pane_transmitter_head_status',
                        'current_heating_pane_receiver_head_status',
                        'temperature_sensor_status',
                        'current_heating_voltage_supply_status',
                        'current_heating_house_status',
                        'current_heating_heads_status',
                        'current_heating_carriers_status',
                        'control_output_laser_power_status',
                        'reserve_status',
                        'temperature_interior',
                        'laser_current_average',
                        'optical_control_voltage_output',
                        'sensor_voltage_supply',
                        'current_heating_pane_transmitter_head',
                        'current_heating_pane_receiver_head',
                        'current_heating_voltage_supply',
                        'current_heating_house',
                        'current_heating_heads',
                        'current_heating_carriers',
                        'number_particles',
                        'number_particles_internal_data',
                        'number_particles_min_speed',
                        'number_particles_min_speed_internal_data',
                        'number_particles_max_speed',
                        'number_particles_max_speed_internal_data',
                        'number_particles_min_diameter',
                        'number_particles_min_diameter_internal_data',
                        'number_particles_no_hydrometeor',
                        'number_particles_no_hydrometeor_internal_data',
                        'number_particles_unknown_classification',
                        'number_particles_unknown_classification_internal_data',
                        'number_particles_class_1',
                        'number_particles_class_1_internal_data',
                        'number_particles_class_2',
                        'number_particles_class_2_internal_data',
                        'number_particles_class_3',
                        'number_particles_class_3_internal_data',
                        'number_particles_class_4',
                        'number_particles_class_4_internal_data',
                        'number_particles_class_5',
                        'number_particles_class_5_internal_data',
                        'number_particles_class_6',
                        'number_particles_class_6_internal_data',
                        'number_particles_class_7',
                        'number_particles_class_7_internal_data',
                        'number_particles_class_8',
                        'number_particles_class_8_internal_data',
                        'number_particles_class_9',
                        'number_particles_class_9_internal_data',
                        ]
        
        df = df.drop(columns = columns_to_drop)
        
        # Some values could be nan
        df = df.dropna()

        return df

    ##------------------------------------------------------------------------.
    #### - Define glob pattern to search data files in raw_dir/data/<station_id>
    raw_data_glob_pattern= "*.txt*"

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
    list_stations_id = ['T1', 'T3']
     

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
                                       column_names=column_names_temp,
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
