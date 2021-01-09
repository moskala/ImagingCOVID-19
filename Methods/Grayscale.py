"""
Module Grayscale contains functions for converting images to grayscale.
# Converting dicom to jpg issue:
# https://github.com/pydicom/pydicom/issues/352
"""

import numpy as np
from pathlib import Path
import pydicom
from pydicom.pixel_data_handlers.util import apply_modality_lut
import PixelArrays
import pylibjpeg
import nibabel as nib


def convert_array_to_grayscale(array):
    """
    Function rescale values of given array between 0-255
    :param array: numpy array
    :return: numpy array converted to grayscale
    """
    # Convert to float to avoid overflow or underflow losses.
    array = array.astype(float)

    # Rescaling grey scale between 0-255
    array -= array.min()
    array *= 255.0 / array.max()

    # Convert to uint
    array_gray = np.uint8(array)

    return array_gray


def convert_array_to_black_white_range(array, black=0, white=255):
    """
    Function rescale array to gray scale.
    :param array: array to be rescaled
    :param black: value correspondent to black level 0
    :param white: value correspondent to white level 1
    :return: rescaled array in gray
    """
    if len(array.shape) > 2:
        return convert_rgb_to_grayscale(array)
    # convert to float to avoid overflow or underflow losses
    arr = array.copy().astype(float)
    diff = np.abs(white - black)
    arr -= (black - 1)
    # values below zero are black
    arr = np.where(arr < 0, 0, arr)
    arr *= 254.0 / diff
    # values above 255 are white
    arr = np.where(arr > 255, 255, arr)
    # convert array to int
    arr = arr.astype(int)
    return arr


def convert_rgb_to_grayscale(array):
    """
    Functions gets array with RGB values and coverts them into grayscale.
    :param array: 3-dim numpy array with RGB values
    :return: 2-dim numpy array with values in 0-255
    """

    if len(array.shape) == 3:
        rgb_weights = [0.2989, 0.5870, 0.1140]
        array_gray = np.dot(array[..., :3], rgb_weights)
        array_gray = np.uint8(array_gray)
        return array_gray
    else:
        return array


def get_grayscale_from_FileDataset(dicomfile):
    """
    Function converts pixel array of dicom file to grayscale and returns is.
    Before conversion Modality LUT operation is applied.
    :param dicomfile: object pydicom.dataset.FileDataset
    :return: numpy array in grayscale
    """
    # Get pixel array
    image = dicomfile.pixel_array
    # Apply Modality LUT or Rescale Operation
    hu = apply_modality_lut(image, dicomfile)
    # Apply conversion to grayscale
    image_gray = convert_array_to_grayscale(hu)

    return image_gray


def get_grayscale_from_dicom(filename: str, src_folder: str):
    """
    Function opens dicom file from given folder and returns it's pixel array in grayscale.
    :param filename: filename of dicom file
    :param src_folder: source folder which contains dicom file
    :return: numpy array in grayscale
    """
    # Crate path for file
    path = Path(src_folder) / filename
    # Read dicom FileDataset
    dcm = pydicom.dcmread(path)
    # Get pixel array in grayscale
    gray_array = get_grayscale_from_FileDataset(dcm)

    return gray_array


def get_grayscale_from_jpg_png(filename: str, src_folder: str):
    """

    :param filename: filename of jpg or png file
    :param src_folder: source folder which contains file
    :return:
    """
    path = Path(src_folder) / filename
    pixel_array = PixelArrays.get_pixel_array_jpg_png(str(path))
    if len(pixel_array.shape) == 3:
        pixel_array = convert_rgb_to_grayscale(pixel_array)
    elif np.max(pixel_array) > 255 or np.min(pixel_array) < 0:
        raise ValueError("Image not in grayscale: {0}".format(path))

    gray_array = get_grayscale_from_normal_array(pixel_array)

    return gray_array


def get_grayscale_from_nifti(filename: str, src_folder: str, global_gray=False):
    """
    Function opens nifti file from given folder and returns it's pixel array in grayscale.
    If global_gray parameter is set to True, values for black and white boundaries are taken from all slices,
    otherwise they are computed for each slice separately.
    :param filename: filename of nifti file
    :param src_folder: source folder which contains file
    :param global_gray: boolean indicator of way to computer white and black boundaries
    :return: numpy array with all slices in grayscale
    """
    # After loading, rescale operation is already applied
    img = nib.load(Path(src_folder) / filename)
    ct_arrays = img.get_fdata()
    ct_arrays = ct_arrays.T
    if global_gray:
        gray_arrays = convert_array_to_grayscale(ct_arrays)
    else:
        gray_arrays = np.array([convert_array_to_grayscale(ct_arrays[i]) for i in range(ct_arrays.shape[0])])

    return gray_arrays


def get_grayscale_from_nifti_slice(filename: str, src_solder: str, slice_number):
    # After loading, rescale operation is already applied
    img = nib.load(Path(src_solder) / filename)
    ct_arrays = img.get_fdata()
    ct_arrays = ct_arrays.T
    gray_array = convert_array_to_grayscale(ct_arrays[slice_number])

    return gray_array


def get_grayscale_from_normal_array(array):
    if np.max(array) <= 1:
        gray_array = 255 * array
        gray_array = gray_array.astype('int')
        return gray_array
    else:
        return array.astype('int')