import os
import SatImg as sat

# Path
proyect_path = os.getcwd()
data_path = proyect_path + '\\eumetsat_data'
file_path = data_path + '\\' + 'W_XX-EUMETSAT-Darmstadt,VIS+IR+IMAGERY,MSG3+SEVIRI_C_EUMG_20171128130009.nc'
# Functions
color_array = sat.color(file_path)
sat.create_image(color_array, path=proyect_path + '\\images', name='Color', extension='jpeg')
print("Color")

colorGeo1_array = sat.latlon(color_array, file=file_path, way=1, interpolation=True)
sat.create_image(colorGeo1_array, path=proyect_path + '\\images', name='ColorGeo Bilinter', extension='jpeg')
print("ColorGeo Bilinter")

colorGeo2_array = sat.latlon(color_array, file=file_path, way=1, interpolation=False)
sat.create_image(colorGeo2_array, path=proyect_path + '\\images', name='ColorGeo', extension='jpeg')
print("ColorGeo")

colorGeo3_array = sat.latlon(color_array, file=file_path, way=2)
sat.create_image(colorGeo3_array, path=proyect_path + '\\images', name='ColorGeo Modo 2', extension='jpeg')
print("ColorGeo Modo 2")
