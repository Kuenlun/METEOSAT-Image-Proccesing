import SatImg as sat
import os

# Path
proyect_path = os.getcwd()
data_path = proyect_path + '\\eumetsat_data'
images_path = proyect_path + '\\images'
file_path = data_path + '\\' + 'W_XX-EUMETSAT-Darmstadt,VIS+IR+IMAGERY,MSG3+SEVIRI_C_EUMG_20171128130009.nc'

# Tell SatImg to read the HDF file
sat.read_file(file_path)

# Making the color array
color_array = sat.color()
sat.create_image(color_array, images_path, 'Color.jpeg')

colorgeo1bilinter_array = sat.latlon(color_array)
sat.create_image(colorgeo1bilinter_array, images_path, 'ColorGeo Bilinter.jpeg')

colorgeo1_array = sat.latlon(color_array, interpolation=False)
sat.create_image(colorgeo1_array, images_path, 'ColorGeo.jpeg')

colorgeo2_array = sat.latlon(color_array, way=2)
sat.create_image(colorgeo2_array, images_path, 'ColorGeo Modo 2.jpeg')
