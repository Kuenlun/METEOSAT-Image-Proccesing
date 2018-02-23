# Converting raw satellite data into images

# Necesary libraries
from netCDF4 import Dataset
import os

os.chdir('eumetsat_data')
file_name = 'W_XX-EUMETSAT-Darmstadt,VIS+IR+IMAGERY,MSG2+SEVIRI_C_EUMG_20070904180010.nc'
dataset = Dataset(os.getcwd() + '\\' + file_name)
print(dataset)
