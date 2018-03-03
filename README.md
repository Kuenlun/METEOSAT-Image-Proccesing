# Converting raw satellite data into images
**This module has been developed for Python3.6**  
The main module is [**SatImg.py**](SatImg.py), is where all the functions are.  
I have also added and example of the usage of the package: [**example.py**](example.py)  
  
## Packages nedded
[h5py](http://www.h5py.org/)    For reading HDF5 files  
[numpy](http://www.numpy.org/)    For working with arrays  
[PIL](https://pillow.readthedocs.io/en/latest/)   For exporting arrays to images  
[Numba](https://numba.pydata.org/)  For speeding up the transformation to geographical coordinates  
  
### Known Errors
**Warnings shown due to the h5py library**  
A future error shows up when reading the hdf file due to the h5py library  

## Explanation of the functions
### **read_file(path)**
**Input:**  
    -**path** (required): The path of file from the MSG 0 deg with the .nc extension:  
e.g:    \eumetsat_data\W_XX-EUMETSAT-Darmstadt,VIS+IR+IMAGERY,MSG2+SEVIRI_C_EUMG_20070904180010.nc  


### **color(red='ch3', green='ch2', blue='ch1')**
Before using it a file must have been read  
**Input:**  
    -**red**: The channel we want to be read  
    -**green**: The channel we want to be green  
    -**blue**: The channel we want to be blue  
**Output:**  
    A numpy (n, m, 3) array with the three channels  


### **dust()**
Before using it a file must have been read  
**Output:**  
    A numpy (n, m, 3) array where:  
    -The first layer is ch10 - ch9  
    -The second layer is ch9 - ch7  
    -The third layer is ch9  
    All of them calculated in a specific way  
    

### **latlon(array, way=1, interpolation=True)**
**Input:**  
    -**array** (required): An array (n, m, 3). Usually the output of the color or dust functions.  
    If the array is not full size (3712, 3712, 3), NaNs arrays will be concatenated  
    It can really be size (n, m, p), where: p >= 1  
    -**way**: An integer  
    If way == 1: Look for the pixel in Geo image that corresponds the satellite image and grab it. This way is the best because we can interpolate the image easily  
    If way == 2: Tell the pixel in the satellite image where to go on the Geo image  
    -**interpolation**: If interpolation is set to True then a bilinear interpolation will be done  
**Output:**  
    A numpy (3712, 3712, 3) array transformed to geographical coordinates  
 
 
### **create_image(array, path, name='MeteosatImage.jpeg')**
**Input:**  
    -**array** (required): The array that is going to be converted into an image  
    -**path** (required): The path where the image will be saved  
    -**name**: The name of the image.  
    JPEG, PNG and TIFF extensions are supported  
