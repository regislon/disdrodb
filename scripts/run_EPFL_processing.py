#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  1 17:18:04 2022

@author: ghiggi
"""
import os
import subprocess
from disdrodb.utils.parser import get_parser_cmd

# You need to set the disdrodb repo path in your .bashrc
# export PYTHONPATH="${PYTHONPATH}:/home/ghiggi/Projects/disdrodb"
# You need to activate the disdrodb envirnment: conda activate disdrodb

# -----------------------------------------------------------------------------.
#### Define campaign dictionary
EPFL_dict = {
    "PARSIVEL_2007": "parser_PARSIVEL_2007.py",
    "GENEPI_2007": "parser_GENEPI_2007.py",
    # "EPFL_ROOF_2008V1": "parser_EPFL_ROOF_2008_V1.py",
    # "EPFL_ROOF_2008V2": "parser_EPFL_ROOF_2008_V2.py",
    "EPFL_ROOF_2011": "parser_EPFL_ROOF_2011.py",
    "EPFL_ROOF_2012": "parser_EPFL_ROOF_2012.py",
    "EPFL_2009": "parser_EPFL_2009.py",
    "DAVOS_2009_2011": "parser_DAVOS_2009_2011.py",
    "HPICONET_2010": "parser_HPICONET_2010.py",
    "COMMON_2011": "parser_COMMON_2011.py",
    "RIETHOLZBACK_2011": "parser_RIETHOLZBACK_2011.py",
    "HYMEX_2012": "parser_HYMEX_2012.py",
    "PARADISO_2014": "parser_PARADISO_2014.py",
    "SAMOYLOV_2017_2019": "parser_SAMOYLOV_2017_2019.py",
    "LOCARNO_2018": "parser_LOCARNO_2018.py",
    "PLATO_2019": "parser_PLATO_2019.py",
}

#### Define filepaths
parser_dir = "/ltenas3/0_Projects/disdrodb/disdrodb/readers/EPFL"
raw_base_dir = "/ltenas3/0_Data/DISDRODB/Raw/EPFL"
processed_base_dir = "/ltenas3/0_Data/DISDRODB/Processed/EPFL"
processed_base_dir = "/tmp/DISDRODB/Processed/EPFL"

#### Processing settings
l0_processing = True
l1_processing = True
force = True
verbose = True
debugging_mode = True
lazy = True
write_zarr = True
write_netcdf = True

#### Process all campaigns
for campaign_name in EPFL_dict.keys():
    parser_filepath = os.path.join(parser_dir, EPFL_dict[campaign_name])
    cmd = get_parser_cmd(
        parser_filepath=parser_filepath,
        raw_dir=os.path.join(raw_base_dir, campaign_name),
        processed_dir=os.path.join(processed_base_dir, campaign_name),
        l0_processing=l0_processing,
        l1_processing=l1_processing,
        write_zarr=write_zarr,
        write_netcdf=write_netcdf,
        force=force,
        verbose=verbose,
        debugging_mode=debugging_mode,
        lazy=lazy,
    )

    subprocess.run(cmd, shell=True)
    # os.system(cmd)

# -----------------------------------------------------------------------------.
# TODO:
# --> Useful to test changes to code do not crash other parser
# --> debuggin_mode=True to speed up tests ;)

# -----------------------------------------------------------------------------.
