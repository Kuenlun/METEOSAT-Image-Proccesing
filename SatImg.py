# Libraries
# Standard library
import os
import math

# Third-party libraries
import h5py             # For reading HDF5 files
import numpy as np      # For working with arrays
from numba import jit   # For speeding the nested loops and arithmetic functions
from PIL import Image   # For exporting arrays to images


# Create the HDF file variable
hdf5_file = None


def read_file(file):
    '''Read the HDF file'''
    global hdf5_file
    hdf5_file = h5py.File(file, 'r')


def read_dataset(ch):
    '''Read and correct the array values by adding the offset and applying
    the scale factor. These values are in the hdf file and are
    different for each channel array'''
    array = np.flip(np.array(hdf5_file[ch]), 0)
    offset = hdf5_file[ch].attrs['add_offset']
    scale = hdf5_file[ch].attrs['scale_factor']
    return (array + offset) * scale


def overlay(array, layer='coast', alpha=0.35):
    '''Given an array, an alpha coeficient and the type of overlay
    we want to make, return a modified aray'''

    # Load the overlay
    os.chdir('overlays')
    if layer[:3] == 'geo':
        geo = True
        layer = layer[4:]
    else:
        geo = False

    if layer == 'coast':
        lay_img = Image.open("msg_0d_full_ir.gif")
    elif layer == 'countries':
        lay_img = Image.open("msg_0d_full_ir_countries.gif")
    elif layer == 'coast-latlon':
        lay_img = Image.open("msg_0d_full_ir_latlong.gif")
    elif layer == 'countries-latlon':
        lay_img = Image.open("msg_0d_full_ir_latlong_countries.gif")
    else:
        print('Error: overlay bad introduced')

    # Convert overlay image into numpy array
    lay_array = np.array(lay_img)
    lay_array = np.expand_dims(lay_array, axis=2)

    # Cut the lay_array in case the array have been cropped
    size = array.shape
    if size[:2] != (3712, 3712):
        # Get array dimensions and position
        south = len(hdf5_file['south_most_line'])
        east = len(hdf5_file['east_most_pixel'])
        north = 3712 - (size[0] + south)
        west = 3712 - (size[1] + east)
        south = 3712 - south
        east = 3712 - east
        lay_array = lay_array[north:south, west:east]

    if geo:
        lay_array = latlon(lay_array, interpolation=False)
        lay_array[np.isnan(lay_array)] = 0
    lay_array = lay_array / lay_array.max()

    # Apply alpha
    # Factor is between 0 and 1, being 0 totally transparent
    lay_array = np.squeeze(lay_array, axis=2)
    array[lay_array == 1] = array[lay_array == 1] * (1 - alpha) + 255 * alpha
    return array


def create_image(array, path, name='MeteosatImage.jpg', layer=None, alpha=0.35):
    '''Create an image given a 3D array (RGB)'''
    if layer is not None:
        array = overlay(array, layer, alpha)
    os.chdir(path)
    Image.fromarray(array.astype('uint8')).save(name)
    print(f'saved: {name}')


def get_brightness(ch, gamma=1):
    '''Get the brightness of the pixels given the temperature'''
    return 255 * ((ch - ch.min()) / (ch.max() - ch.min()))**(1 / gamma)


# List of coefficients used for calculing the temperature
c1 = 1.19104 * 10**(-5)
c2 = 1.43877
coefficients = {
    'ch4': {'Channel_ID': 'IR 3.9', 'vc': 2569.094, 'a': 0.9959, 'b': 3.471},
    'ch5': {'Channel_ID': 'WV 6.2', 'vc': 1598.566, 'a': 0.9963, 'b': 2.219},
    'ch6': {'Channel_ID': 'WV 7.3', 'vc': 1362.142, 'a': 0.9991, 'b': 0.485},
    'ch7': {'Channel_ID': 'IR 8.7', 'vc': 1149.083, 'a': 0.9996, 'b': 0.181},
    'ch8': {'Channel_ID': 'IR 9.7', 'vc': 1034.345, 'a': 0.9999, 'b': 0.060},
    'ch9': {'Channel_ID': 'IR 10.8', 'vc': 930.659, 'a': 0.9983, 'b': 0.627},
    'ch10': {'Channel_ID': 'IR 12.0', 'vc': 839.661, 'a': 0.9988, 'b': 0.397},
    'ch11': {'Channel_ID': 'IR 13.4', 'vc': 752.381, 'a': 0.9981, 'b': 0.576}
}


def get_temperature(ch, str_ch):
    '''Convert radiance into temperature in Kelvin'''
    # Ignore the zero division and log of negative numbers warning
    np.seterr(divide='ignore', invalid='ignore')
    oper = c1 * coefficients[str_ch]['vc']**3 / ch + 1
    oper[np.isinf(oper)] = np.nan
    return (c2 * coefficients[str_ch]['vc'] / np.log(oper) - coefficients[str_ch]['b']) / coefficients[str_ch]['a']


def color(red='ch3', green='ch2', blue='ch1'):
    '''Make an array of the coloured image'''
    # Checkings
    channels = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10', 'ch11']
    if red in channels and green in channels and blue in channels:
        # Reading the datasets of the channels
        chR = read_dataset(red)
        chG = read_dataset(green)
        chB = read_dataset(blue)
        # Maping the radiance values from 0 to 255
        chR = get_brightness(chR)
        chG = get_brightness(chG)
        chB = get_brightness(chB)
        # Creating the RGB matrix (make 3D array and change data type to int)
        return np.dstack((chR, chG, chB))
    else:
        if red not in channels:
            raise NameError(f'Channel "{red}" is not defined')
        if green not in channels:
            raise NameError(f'Channel "{green}" is not defined')
        if blue not in channels:
            raise NameError(f'Channel "{blue}" is not defined')


def dust():
    '''Make an array of the dust image'''

    # Reading the datasets of the channels
    ch7 = read_dataset('ch7')
    ch9 = read_dataset('ch9')
    ch10 = read_dataset('ch10')
    # Getting the temperature
    ch7_temp = get_temperature(ch7, 'ch7')
    ch9_temp = get_temperature(ch9, 'ch9')
    ch10_temp = get_temperature(ch10, 'ch10')
    # Create the pre red, green and blue arrays
    chR_temp = ch10_temp - ch9_temp
    chG_temp = ch9_temp - ch7_temp
    chB_temp = ch9_temp
    # Dealing with the NaNs
    chR_temp[np.isnan(chR_temp)] = -4
    chG_temp[np.isnan(chG_temp)] = 0
    chB_temp[np.isnan(chB_temp)] = 261
    # Stablishing the ranges
    chR_temp[chR_temp < -4] = -4
    chR_temp[chR_temp > 2] = 2
    chG_temp[chG_temp < 0] = 0
    chG_temp[chG_temp > 15] = 15
    chB_temp[chB_temp < 261] = 261
    chB_temp[chB_temp > 289] = 289
    # Getting the brigtness
    chR = get_brightness(chR_temp, gamma=1)
    chG = get_brightness(chG_temp, gamma=2.5)
    chB = get_brightness(chB_temp, gamma=1)
    # Creating the RGB matrix (make 3D array and change data type to int)
    return np.dstack((chR, chG, chB))


############################################################################
# The following functions are used to get the transformation to Geo coords #
############################################################################

# Constants used for the transformation
coff = 1856
loff = 1856
cfac = -781648343.404
lfac = -781648343.404
sat_height = 42164.0
sub_lon = 0.0
r_eq = 6378.169
r_pol = 6356.5838


@jit(nopython=True)
def pix2geo(col, row):
    '''Return the latitude and longitude of an MSG image
    for a given pair of pixel column and row.
    (based on the formulas given in Ref. [1])'''

    # Calculate viewing angle of the satellite by use of the equation
    # on page 28, Ref [1].
    x = 2**16 * (col - coff) / cfac
    y = 2**16 * (row - loff) / lfac
    # Now calculate the inverse projection
    # first check for visibility, whether the pixel is located on the Earth
    # surface or in space.
    # To do this calculate the argument to sqrt of "sd", which is named "sa".
    # If it is negative then the sqrt will return NaN and the pixel will be
    # located in space, otherwise all is fine and the pixel is located on the
    # Earth surface.
    sa = np.power((sat_height * np.cos(x) * np.cos(y)), 2) - (np.cos(y) * np.cos(y) + 1.006803 * np.sin(y) * np.sin(y)) * 1737121856
    # Produce error values
    if sa <= 0.0:
        latitude = np.nan
        longitude = np.nan
        return latitude, longitude
    # Now calculate the rest of the formulas using equations on
    # page 25, Ref. [1]
    sd = np.sqrt(np.power((sat_height * np.cos(x) * np.cos(y)), 2) - (np.cos(y) * np.cos(y) + 1.006803 * np.sin(y) * np.sin(y)) * 1737121856)
    sn = (sat_height * np.cos(x) * np.cos(y) - sd) / (np.cos(y) * np.cos(y) + 1.006803 * np.sin(y) * np.sin(y))
    s1 = sat_height - sn * np.cos(x) * np.cos(y)
    s2 = sn * np.sin(x) * np.cos(y)
    s3 = -sn * np.sin(y)
    sxy = np.sqrt(s1 * s1 + s2 * s2)
    # Using the previous calculations the inverse projection can be
    # calculated now, which means calculating the lat. / long. from
    # the pixel row and column by equations on page 25, Ref[1].
    longi = np.arctan(s2 / s1) + sub_lon
    lati = np.arctan((1.006803 * s3) / sxy)
    # Convert from radians into degrees
    latitude = lati * 180 / np.pi
    longitude = longi * 180 / np.pi
    return latitude, longitude


@jit(nopython=True)
def geo2pix(lati, longi):
    '''Return the pixel column and line of an MSG image
    for a given pair of latitude/longitude.
    (based on the formulas given in Ref. [1]) '''

    # Check if the values are sane, otherwise return error values
    if lati < -90.0 or lati > 90.0 or longi < -180.0 or longi > 180.0:
        row = np.nan
        col = np.nan
        return row, col
    # Convert them to radiants
    lat = lati * np.pi / 180
    lon = longi * np.pi / 180
    # Calculate the geocentric latitude from the
    # geograhpic one using equations on page 24, Ref. [1]
    c_lat = np.arctan(0.993243 * (np.sin(lat) / np.cos(lat)))
    # Using c_lat calculate the length form the Earth
    # centre to the surface of the Earth ellipsoid
    # equations on page 23, Ref. [1]
    re = r_pol / np.sqrt((1 - 0.00675701 * np.cos(c_lat) * np.cos(c_lat)))
    # Calculate the forward projection using equations on
    # page 24, Ref. [1]
    rl = re
    r1 = sat_height - rl * np.cos(c_lat) * np.cos(lon - sub_lon)
    r2 = - rl * np.cos(c_lat) * np.sin(lon - sub_lon)
    r3 = rl * np.sin(c_lat)
    rn = np.sqrt(r1 * r1 + r2 * r2 + r3 * r3)
    # Check for visibility, whether the point on the Earth given by the
    # latitude / longitude pair is visible from the satellte or not. This
    # is given by the dot product between the vectors of:
    # 1) the point to the spacecraft,
    # 2) the point to the centre of the Earth.
    # If the dot product is positive the point is visible otherwise it
    # is invisible.
    dotprod = r1 * (rl * np.cos(c_lat) * np.cos(lon - sub_lon)) - r2 * r2 - r3 * r3 * (np.power((r_eq / r_pol), 2))
    if dotprod <= 0:
        row = np.nan
        col = np.nan
        return row, col
    # The forward projection is x and y
    xx = np.arctan((-r2 / r1))
    yy = np.arcsin((-r3 / rn))
    # Convert to pixel column and row using the scaling functions on
    # page 28, Ref. [1]. And finding nearest integer value for them.
    col = coff + xx * np.power(2, -16.0) * cfac
    row = loff + yy * np.power(2, -16.0) * lfac
    return row, col


@jit(nopython=True)
def bilinter(array, place):
    '''Calculate the bilinear interpolation
    given an array and some coordinates (float)'''

    # Get surounding values
    x = place[0]
    y = place[1]
    xf = math.floor(x)
    yf = math.floor(y)
    a = array[xf, yf, :]
    b = array[xf + 1, yf, :]
    c = array[xf, yf + 1, :]
    d = array[xf + 1, yf + 1, :]
    if np.isnan(np.concatenate((a, b, c, d), axis=0)).any():
        value = np.empty((array.shape[2]))
        value[:] = np.nan
        return value
    # Interpolate
    x1 = (b - a) * (x - xf) + a
    x2 = (d - c) * (x - xf) + c
    value = (x2 - x1) * (y - yf) + x1
    return value


@jit(nopython=True)
def geo1bilinter(array):
    # Create the empty geo array
    size = array.shape
    geo_array = np.empty(size)
    geo_array[:] = np.nan
    for row in range(3712):
        for col in range(3712):
            ro = 30 * (2 * row - 3711) / 1237
            co = 30 * (3711 - 2 * col) / 1237
            pix = geo2pix(ro, co)
            if not math.isnan(pix[0]):
                value = bilinter(array, pix)
                geo_array[row, col, :] = value
    return geo_array


@jit(nopython=True)
def geo1(array):
    # Create the empty geo array
    size = array.shape
    geo_array = np.empty(size)
    geo_array[:] = np.nan
    for row in range(3712):
        for col in range(3712):
            ro = 30 * (2 * row - 3711) / 1237
            co = 30 * (3711 - 2 * col) / 1237
            pix = geo2pix(ro, co)
            if not math.isnan(pix[0]):
                geo_array[row, col, :] = array[int(pix[0]), int(pix[1]), :]
    return geo_array


@jit(nopython=True)
def geo2(array):
    # Create the empty geo array
    size = array.shape
    geo_array = np.empty(size)
    geo_array[:] = np.nan
    for row in range(3712):
        for col in range(3712):
            pix = pix2geo(row, col)
            if math.isnan(pix[0]):
                continue
            ro = int((pix[0] + 90) * (1237) / 60)
            co = int((-pix[1] + 90) * (1237) / 60)
            geo_array[ro, co, :] = array[col, row, :]
    return geo_array


def latlon(array, way=1, interpolation=True):
    '''Create a latitude and longitude array from a rgb array.
    The given array can be for example the color return array'''
    # First of all we need to know the position of the taken image
    size = array.shape
    if size[:2] != (3712, 3712):
        # In case the array has been cutted fill it with NaNs
        # until we have the full 3712x3712 array
        south = len(hdf5_file['south_most_line'])
        east = len(hdf5_file['east_most_pixel'])
        north = size[0] + south - 1
        west = size[1] + east - 1

        up = np.empty((3712 - north, size[1], size[2]))
        up[:] = np.nan
        array = np.concatenate((up, array), axis=0)

        down = np.empty((south - 1, size[1], size[2]))
        down[:] = np.nan
        array = np.concatenate((array, down), axis=0)

        size = array.shape
        left = np.empty((size[0], 3712 - west, size[2]))
        left[:] = np.nan
        array = np.concatenate((left, array), axis=1)

        right = np.empty((size[0], east - 1, size[2]))
        right[:] = np.nan
        array = np.concatenate((array, right), axis=1)
    if way == 1:
        # Look for the pixel in Geo image that corresponds the
        # satellite image and grab it. This way is the best because
        # we can interpolate the image easily
        if interpolation:
            geo_array = geo1bilinter(array)
        else:
            geo_array = geo1(array)
    elif way == 2:
        # Tell the pixel in the satellite image where to go on the
        # Geo image
        geo_array = geo2(array)
    return geo_array
