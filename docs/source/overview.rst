========
Overview
========

DISDRODB: A global database of raindrop size distribution observations



Motivation
=====
The raindrop size distribution (DSD) describes the concentration and size distributions of raindrops in a volume of air. It is a crucial piece of  information to model the propagation of microwave signals through the atmosphere (key for telecommunication and weather radar remote sensing calibration), to improve microphysical schemes in numerical weather prediction models, and to understand land surface processes (rainfall interception, soil erosion). 

The need for understanding the DSD spatio-temporal variability has led scientists all around the globe to “count the drops” by deploying DSD recording instruments known as disdrometers. Numerous measurement campaigns have been run by various meteorological services, national agencies (e.g. the NASA Precipitation Measurement Mission - PMM - Science Team), and university research groups. However, only a small fraction of those data is easily accessible. Data are stored in disparate formats with poor documentation, making them difficult to share, analyse, compare and re-use.  Additionally, very limited software is currently publicly available for DSD processing.


Products levels 
=====
DISDRODB is planned to be composed of 3 product levels: L0A, L0B and L1.

* L0A provides the raw measurements converted into a standardized netCDF format.
* L0B provides homogenized and quality-checked data
* L1 provides scientific products derived from the L0 data.



Project structure 
=====
    
Here is an overview of the project structure : 

| disdrodb/
| ├── L0/
| │   ├── readers  
| │   │   ├── *.py                  
| │   ├── L0A/
| │   │   ├── auxiliary.py  
| │   │   ├── issue.py  
| │   │   ├── processing.py  
| │   │   ├── utils_nc.py  
| │   ├── L0B/
| ├── utils/
| ├── configs/
| │   ├── <devices>/
| │   │   ├── *.yml 
| ├── check_standards.py
| ├── data_encodings.py
| ├── dev_tool.py
| ├── io.py
| ├── L0_proc.py
| ├── L1_proc.py
| ├── logger.py
| ├── metadata.py
| ├── standard.py
| docs/
| tests/
| data/
| templates/
| scripts/
| .gitignore
| LICENSE
| CONTRIBUTING.md
| README.md
| requirements.txt



Files description : 

**readers/\*.py** : Current readers (parsers) to transform raw data into a standardize Apache parquet file.  *RL : should use "pasrer" or "reader" -> to rename*

**L0A/auxiliary.py** : Define dictionary mapping for ARM and DIVEN standard *RL : to move into specific reader or utils ? *

**L0A/issue.py** : Create an Yml issue file to exclue time related error while reading raw data *RL : to move into  utils ? *

**L0A/processing.py** :  *RL : is this file used ? *

**L0A/utils_nc.py** :  Define specific functions for ARM and DIVEN standard *RL : to move into specific reader or utils ? *

**templates/\*.py** : Template to create new pasrser

**scripts/\*.py** :  Script to batch processing compains 

**check_standards.py** : Data quality function *RL : to move into  utils ?  rename ?*

**data_encodings.py** : Define the encoding of parquet column *RL : to move into  utils ?  rename ? Not used in any readers ?*

**dev_tool.py** : Functions to help the developer to create a format specific reader *RL : to move into  utils ?  rename ? Not used in any readers ?*

**io.py** : Functions to translate raw data into into a standardize Apache parquet file *RL : to move into utils, rename ? *

**L0_proc.py** : Process the translation from raw data into into a standardize Apache parquet file *Move into L0A*

**L1_proc.py** : Process the translation from standardize Apache parquet file into netCDF. *Move into L0B*

**logger.py** : Create log file. *Move into utils*

**metadata.py** : Create, reader metadata fo reader *Move into utils ?*

**standard.py** : Retrive devices characteritics *Move into utils ?*






tackle the dev issue