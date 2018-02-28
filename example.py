import SatImg as sat
import os


# Path
proyect_path = os.getcwd()
data_path = proyect_path + '\\eumetsat_data'
images_path = proyect_path + '\\images'
file_path = data_path + '\\' + 'W_XX-EUMETSAT-Darmstadt,VIS+IR+IMAGERY,MSG3+SEVIRI_C_EUMG_20171128130009.nc'


# Tell SatImg to read the HDF file
sat.read_file(file_path)

# Functions
color_array = sat.color()
sat.create_image(color_array, path=images_path, name='Color', extension='jpeg')
print("Color")

colorGeo1_array = sat.latlon(color_array, way=1, interpolation=True)
sat.create_image(colorGeo1_array, path=images_path, name='ColorGeo Bilinter', extension='jpeg')
print("ColorGeo Bilinter")

colorGeo2_array = sat.latlon(color_array, way=1, interpolation=False)
sat.create_image(colorGeo2_array, path=images_path, name='ColorGeo', extension='jpeg')
print("ColorGeo")

colorGeo3_array = sat.latlon(color_array, way=2)
sat.create_image(colorGeo3_array, path=images_path, name='ColorGeo Modo 2', extension='jpeg')
print("ColorGeo Modo 2")
