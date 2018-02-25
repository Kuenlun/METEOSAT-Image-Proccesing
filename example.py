import os
import Sat_Img as sat

proyect_path = os.getcwd()
data_path = proyect_path + '\\eumetsat_data'
file_path = data_path + '\\' + 'W_XX-EUMETSAT-Darmstadt,VIS+IR+IMAGERY,MSG2+SEVIRI_C_EUMG_20070904180010.nc'

color_array = sat.color(file_path)
sat.create_image(color_array, path=proyect_path + '\\images', name='Color', extension='jpeg')
dust_array = sat.dust(file_path)
sat.create_image(dust_array, path=proyect_path + '\\images', name='Dust', extension='jpeg')
