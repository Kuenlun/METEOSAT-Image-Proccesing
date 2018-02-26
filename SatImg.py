# Necesary libraries
import h5py             # For reading HDF5 files
import numpy as np      # For working with arrays
from PIL import Image   # For exporting arrays to images
import os


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


def read_dataset(ch, hdf5_file):
    '''Read and correct the array values by adding the offset and applying
    the scale factor. These values are in the hdf file and are
    different for each channel array'''
    array = np.flip(np.array(hdf5_file[ch]), 0)
    offset = hdf5_file[ch].attrs['add_offset']
    scale = hdf5_file[ch].attrs['scale_factor']
    return (array + offset) * scale


def get_brightness(ch, gamma=1):
    '''Get the brightness of the pixels given the temperature'''
    return 255 * ((ch - ch.min()) / (ch.max() - ch.min()))**(1 / gamma)


def get_temperature(ch, str_ch):
    '''Convert radiance into temperature in Kelvin'''
    # Ignore the zero division and log of negative numbers warning
    np.seterr(divide='ignore', invalid='ignore')
    oper = c1 * coefficients[str_ch]['vc']**3 / ch + 1
    oper[np.isinf(oper)] = np.nan
    return (c2 * coefficients[str_ch]['vc'] / np.log(oper) - coefficients[str_ch]['b']) / coefficients[str_ch]['a']


def create_image(array, path, name='MeteosatImage', extension='jpeg'):
    '''Create an image given a 3D array (RGB)'''
    os.chdir(path)
    image_name = name + '.' + extension
    Image.fromarray(array.astype('uint8')).save(image_name)


def color(file, red='ch3', green='ch2', blue='ch1'):
    '''Make an array of the coloured image'''
    # Checkings
    channels = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10', 'ch11']
    if red in channels and green in channels and blue in channels:
        # Reading the file
        hdf5_file = h5py.File(file, 'r')
        # Reading the datasets of the channels
        chR = read_dataset(red, hdf5_file)
        chG = read_dataset(green, hdf5_file)
        chB = read_dataset(blue, hdf5_file)
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


def dust(file):
    '''Make an array of the dust image'''
    # Reading the file
    hdf5_file = h5py.File(file, 'r')
    # Reading the datasets of the channels
    ch7 = read_dataset('ch7', hdf5_file)
    ch9 = read_dataset('ch9', hdf5_file)
    ch10 = read_dataset('ch10', hdf5_file)
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


def latlon(array, file=None):
    '''Create a latitude and longitude array from a rgb array.
    The given array can be for example the color return array'''
    # First of all we need to know the position of the taken image
    if file is None:
        # We asume the array is full-size (3712x3712)
        pass
    else:
        # In case the array has been cutted
        hdf5_file = h5py.File(file, 'r')
        south = len(hdf5_file['south_most_line'])
        east = len(hdf5_file['east_most_pixel'])
        size = array.shape
        full_size = 3712
        north = size[0] + south - 1
        west = size[1] + east - 1

        up = np.empty((full_size - north, size[1], 3))
        up[:] = np.nan
        array = np.concatenate((up, array), axis=0)

        down = np.empty((south - 1, size[1], 3))
        down[:] = np.nan
        array = np.concatenate((array, down), axis=0)

        size = array.shape
        left = np.empty((size[0], full_size - west, 3))
        left[:] = np.nan
        array = np.concatenate((left, array), axis=1)

        right = np.empty((size[0], east - 1, 3))
        right[:] = np.nan
        array = np.concatenate((array, right), axis=1)


proyect_path = os.getcwd()
data_path = proyect_path + '\\eumetsat_data'
file_path = data_path + '\\' + 'W_XX-EUMETSAT-Darmstadt,VIS+IR+IMAGERY,MSG2+SEVIRI_C_EUMG_20070904180010.nc'
color_array = color(file_path)
latlon(color_array, file=file_path)
