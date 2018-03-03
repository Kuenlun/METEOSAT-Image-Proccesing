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
sat.create_image(color_array, images_path, 'Color.jpeg', layer='countries', alpha=0.35)

colorgeo1bilinter_array = sat.latlon(color_array)
sat.create_image(colorgeo1bilinter_array, images_path, 'ColorGeo Bilinter.jpeg', layer='geo-countries', alpha=0.35)

colorgeo1_array = sat.latlon(color_array, interpolation=False)
sat.create_image(colorgeo1_array, images_path, 'ColorGeo.jpeg', layer='geo-countries', alpha=0.35)

colorgeo2_array = sat.latlon(color_array, way=2)
sat.create_image(colorgeo2_array, images_path, 'ColorGeo Modo 2.jpeg', layer='geo-countries', alpha=0.35)


# Making the dust array
dust_array = sat.dust()
sat.create_image(dust_array, images_path, 'Dust.jpeg', layer='countries', alpha=0.35)

dustgeo1bilinter_array = sat.latlon(dust_array)
sat.create_image(dustgeo1bilinter_array, images_path, 'DustGeo Bilinter.jpeg', layer='geo-countries', alpha=0.35)

dustgeo1_array = sat.latlon(dust_array, interpolation=False)
sat.create_image(dustgeo1_array, images_path, 'DustGeo.jpeg', layer='geo-countries', alpha=0.35)

dustgeo2_array = sat.latlon(dust_array, way=2)
sat.create_image(dustgeo2_array, images_path, 'DustGeo Modo 2.jpeg', layer='geo-countries', alpha=0.35)
