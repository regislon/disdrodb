#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 07:29:20 2022

@author: kimbo
"""

def create_metadata(fpath, data):
    """Create default YAML metadata file."""
    import yaml
    
    with open(fpath, "w+") as f:
        yaml.dump(data, f, sort_keys=False)


def create_list_path(df, folder_output_path):
    '''Return list of yaml file path from DSD metadata.csv dataframe'''
    # Dataframe for files
    df_struc = df.iloc[:,:3]
    df_struc.columns = ['inst','camp','id']
    df_struc = df_struc.fillna('missing_id')

    # df_struc['inst'].unique()

    # Create structure folder
    list_path = []

    import os

    for i, r in df_struc.iterrows():
        
        path = os.path.join(folder_output_path, r['inst'], r['camp'], 'metadata', r['id'] + '.yml')
        
        list_path.append(path)
        
        # if not isinstance(path, str):
        #     raise TypeError("'path' must be a strig.")
        # try:
        #     os.makedirs(path)
        # except FileExistsError:
        #     pass
    
    return list_path

def create_list_meta(df):
    '''Return list for yaml dump'''
    # Remove useless columns
    df = df.iloc[:,3:]
    df = df.drop(columns = ['comment'])

    # Reset index
    df = df.reset_index(drop=True)
    
    list_meta = df.to_dict('records')
    
    return list_meta


def create_metadata_files(list_path, list_meta):
    '''Create all the metadata files'''
    import os
    
    for i in range(len(list_meta)):
        os.makedirs(os.path.dirname(list_path[i]), exist_ok=True)
        create_metadata(list_path[i], list_meta[i])
        
def clean_df(df):
    '''Clean the dataframe by comments into DSD metadata.csv'''
    # Drop roww without metadata (comments into the drive sheet)
    df = df.dropna(thresh=10)

    # Replace nan
    values = {"Id dispositivo": 'missing_id',"latitude": -9999, "longitude": -9999, "altitude": -9999}
    df = df.fillna(value=values)
    df = df.fillna('')
    
    return df

import pandas as pd 

# Path for DSD metadata.csv
source_path = '/home/kimbo/Desktop/DSD metadata.csv'

# Output folder for the metadata
folder_output_path = '/home/kimbo/data/metadata_test'

df = pd.read_csv(source_path)

df = clean_df(df)

list_path = create_list_path(df, folder_output_path)

list_meta = create_list_meta(df)

create_metadata_files(list_path, list_meta)


