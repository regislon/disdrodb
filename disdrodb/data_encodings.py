#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


def get_L0_dtype_standards():
    from disdrodb.standards import get_L0_dtype

    # TODO: TO REFACTOR !!!!
    dtype_dict = {
        # Disdronet raspberry variables
        "epoch_time": "float32",
        "time": "M8[s]",
        "id": "uint32",
        # Datalogger variables
        "datalogger_heating_current": "float32",
        "datalogger_battery_voltage": "float32",
        "datalogger_temperature": "object",
        "datalogger_voltage": "object",
        "datalogger_error": "uint8",
        # Coords
        "latitude": "float32",
        "longitude": "float32",
        "altitude": "float32",
        # Custom fields
        "Unknow_column": "object",
        # Temp variables
        "temp": "object",
        "TEMPORARY": "object",
        "TO_BE_MERGE": "object",
        "TO_BE_MERGE2": "object",
        "TO_BE_PARSED": "object",
        "TO_BE_SPLITTED": "object",
        "TO_DEBUG": "object",
        "Debug_data": "object",
        "All_0": "object",
        "error_code?": "object",
        "unknow2": "object",
        "unknow3": "object",
        "unknow4": "object",
        "unknow5": "object",
        "unknow": "object",
        "unknow6": "object",
        "unknow7": "object",
        "unknow8": "object",
        "unknow9": "object",
        "power_supply_voltage": "object",
        "A_voltage2?": "object",
        "A_voltage?": "object",
        "All_nan": "object",
        "All_5000": "object",
    }
    d1 = get_L0_dtype(sensor_name="OTT_Parsivel")
    dtype_dict.update(d1)
    return dtype_dict


#### Dictionary to convert ARM netcdf to L1 standard
# - Use to rename the ARM keys to L1 standard
def get_ARM_to_l0_dtype_standards():

    dict_ARM_to_l0 = {  # Norway
        "alt": "altitude",
        "class_size_width": "class_size_width_OldName",
        "diameter_max": "diameter_max_OldName",
        "diameter_min": "diameter_min_OldName",
        "equivalent_radar_reflectivity": "equivalent_radar_reflectivity_OldName",
        "equivalent_radar_reflectivity_ott": "reflectivity_32bit",
        "fall_velocity_calculated": "fall_velocity_calculated_OldName",
        "heating_current": "sensor_heating_current",
        "intercept_parameter": "intercept_parameter_OldName",
        "laserband_amplitude": "laser_amplitude",
        "lat": "latitude",
        "liquid_water_content": "liquid_water_content_OldName",
        "liquid_water_distribution_mean": "liquid_water_distribution_mean_OldName",
        "lon": "longitude",
        "median_volume_diameter": "median_volume_diameter_OldName",
        "moment1": "moment1_OldName",
        "moment2": "moment2_OldName",
        "moment3": "moment3_OldName",
        "moment4": "moment4_OldName",
        "moment5": "moment5_OldName",
        "moment6": "moment6_OldName",
        "mor_visibility": "mor_visibility_OldName",
        "number_density_drops": "number_density_drops_OldName",
        "number_detected_particles": "n_particles",
        "precip_rate": "rain_rate_32bit",
        "qc_equivalent_radar_reflectivity_ott": "qc_equivalent_radar_reflectivity_ott_OldName",
        "qc_heating_current": "qc_heating_current_OldName",
        "qc_laserband_amplitude": "qc_laserband_amplitude_OldName",
        "qc_mor_visibility": "qc_mor_visibility_OldName",
        "qc_number_detected_particles": "qc_number_detected_particles_OldName",
        "qc_precip_rate": "qc_precip_rate_OldName",
        "qc_sensor_voltage": "qc_sensor_voltage_OldName",
        "qc_snow_depth_intensity": "qc_snow_depth_intensity_OldName",
        "qc_weather_code": "qc_weather_code_OldName",
        "raw_spectrum": "raw_spectrum_OldName",
        "sensor_temperature": "sensor_temperature",
        "sensor_voltage": "sensor_battery_voltage",
        "slope_parameter": "slope_parameter_OldName",
        "snow_depth_intensity": "snow_depth_intensity_OldName",
        "time": "time",
        "time_offset": "time_offset_OldName",
        "weather_code": "weather_code_SYNOP_4680",
        # ARM Mobile Facility
        "base_time": "time",
        # Alaska
    }

    return dict_ARM_to_l0


#### Dictionary to convert DIVEN netcdf to L1 standard
# - Use to rename the DIVEN keys to L1 standard
def get_DIVEN_to_l0_dtype_standards():

    dict_DIVEN_to_l0 = {
        "time": "time",
        "latitude": "latitude",
        "longitude": "longitude",
        "diameter": "diameter_OldName",
        "fallspeed": "fallspeed_OldName",
        "qc_flag": "qc_flag_OldName",
        "precipitation_flux": "precipitation_flux_OldName",
        "solid_precipitation_flux": "solid_precipitation_flux_OldName",
        "precipitation_visibility": "precipitation_visibility_OldName",
        "reflectivity": "reflectivity_16bit",
        "measurement_quality": "measurement_quality_OldName",
        "present_weather_1m": "present_weather_1m_OldName",
        "present_weather_5m": "present_weather_5m_OldName",
        "hydrometeor_type_1m": "hydrometeor_type_1m_OldName",
        "hydrometeor_type_5m": "hydrometeor_type_5m_OldName",
        "max_hail_diameter": "max_hail_diameter_OldName",
        "particle_count": "n_particles_all",
        "year": "year_OldName",
        "month": "month_OldName",
        "day": "day_OldName",
        "hour": "hour_OldName",
        "minute": "minute_OldName",
        "second": "second_OldName",
        "day_of_year": "day_of_year_OldName",
        "size_velocity_distribution": "size_velocity_distribution_OldName",
        "drop_size_distribution": "drop_size_distribution_OldName",
        "drop_velocity_distribution": "drop_velocity_distribution_OldName",
    }

    return dict_DIVEN_to_l0


def get_L1_dtype():
    # Float 32 or Float 64 (f4, f8)
    # (u)int 8 16, 32, 64   (u/i  1 2 4 8)
    dtype_dict = {
        "FieldN": "float32",
        "FieldV": "float32",
        "RawData": "int64",  # TODO: uint16? uint32 check largest number occuring, and if negative
    }
    return dtype_dict


def get_dtype_standards_all_object():
    dtype_dict = get_L0_dtype_standards()
    for i in dtype_dict:
        dtype_dict[i] = "object"

    return dtype_dict
