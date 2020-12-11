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


def get_grayscale_from_jpg_png(filename: str, src_solder: str):
    """

    :param filename:
    :param src_solder:
    :return:
    """
    path = Path(src_solder) / filename
    pixel_array = PixelArrays.get_pixel_array_jpg_png(str(path))
    gray_array = convert_rgb_to_grayscale(pixel_array)
    return gray_array


def get_grayscale_from_nifti():
    raise NotImplementedError("Needs to be added")
    img = nib.load('my_image.nii')
    print(img.dataobj.slope, img.dataobj.inter)


def get_grayscale_from_jpg_png(array):
    """
    Converts jpg and png files to grayscale.
    :param array:
    :return:
    """
    array = convert_rgb_to_grayscale(array)
    array = convert_rgb_to_grayscale(array)

    return array
