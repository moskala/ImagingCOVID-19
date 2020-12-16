"""
Module for checking in which computer tomography window  array values are
https://www.radiologycafe.com/medical-students/radiology-basics/ct-overview
"""

from pathlib import Path
import numpy as np
from enum import Enum
import pydicom
from pydicom.pixel_data_handlers.util import apply_modality_lut
import Grayscale as gray


class CTWindow(Enum):
    """
    Enum class representing different types of window in computer tomography.
    """
    SoftTissueWindow = 0
    LungWindow = 1
    BoneWindow = 2
    GrayscaleWindow = 3

    def __str__(self):
        dictionary = {
            0: "Soft Tissue Window",
            1: "Lung Window",
            2: "Bone Window",
            3: "Grayscale"
        }
        return dictionary[self.value]


# Przedziały wartości dla poszczególnych typów okna, ważna kolejność!
# intervals = {
#   CTWindow.GrayscaleWindow: (0, 255),
#   CTWindow.SoftTissueWindow: (-125, 225),
#   CTWindow.BoneWindow: (-700, 1300),
#   CTWindow.LungWindow: (-1350, 150)
#   # CTWindow.LungWindow: (-1200, 800),
# }

# types of CT windows with levels and widths
CT_windows_parameters = {
  CTWindow.GrayscaleWindow: (127.5, 255),
  CTWindow.SoftTissueWindow: (50, 350),
  CTWindow.LungWindow: (-600, 1500),
  CTWindow.BoneWindow: (300, 2000),
}


def get_window_parameters(ct_window_type):
    """
    Functions gets ct window parameters for given window type. If given type does not exist, None is returned
    :param ct_window_type: CT window type
    :return: tuple (level, width) with parameters of given window type
    """
    if ct_window_type in CT_windows_parameters:
        return CT_windows_parameters[ct_window_type]
    else:
        return None


def get_window_range(ct_window_type):
    """
    Functions gets ct window range for given window type. If given type does not exist, None is returned
    :param ct_window_type: CT window type
    :return: tuple (lower_bound, upper_bound) represents given window type range
    """
    if ct_window_type in CT_windows_parameters:
        level, width = CT_windows_parameters[ct_window_type]
        lower_bound = level - width / 2
        upper_bound = level + width / 2
        return lower_bound, upper_bound
    else:
        return None


def check_array_window(array):
    """
    Function checks in which CT window array values are.
    :param array: 2-dim numpy array
    :return: type of CTWindow which correspond with array values with min and max value
    or None if no match is found
    """
    min_val = np.min(array)
    max_val = np.max(array)
    w = None
    
    # Function goes from the smallest interval
    for window in CTWindow:
        lower_bound, upper_bound = get_window_range(window)
        if (min_val >= lower_bound) & (max_val <= upper_bound):
            w = window
            break

    return w, min_val, max_val


def cut_array_to_lung_window(array, width=None, center=None):
    """
    Function cuts values outside specified LungWindow interval.
    :param array: numpy array representing pixel array
    :param center: CT window center value
    :param width: CT window width value
    :return: numpy array which has values are subset of LungWindow interval
    """
    if width is None or center is None:
        lower_bound, upper_bound = get_window_range(CTWindow.LungWindow)
    else:
        lower_bound = center - width / 2
        upper_bound = center + width / 2
    
    array = np.where(array < lower_bound, lower_bound, array)
    array = np.where(array > upper_bound, upper_bound, array)
    
    return array


def check_array_window_or_cut(array):
    """
    Function checks in which CT window array values are and cuts to LungWindow if possible.
    :param array: numpy array representing pixel array
    :return: tuple (ct_window, array) where ct_window is final CTWindow type
    and array is numpy array representing final pixel array
    """
    ct_window, min_val, max_val = check_array_window(array)
    
    if ct_window is None or ct_window is CTWindow.BoneWindow:
        array = cut_array_to_lung_window(array)
        ct_window, min_val, max_val = check_array_window(array)
    return ct_window, array


def get_array_dicom_lut(file, folder):
    """
    Function reads given dicom file and applies LUT modality operation
    in order to get pixel values in Hounsfield units.
    :param file: name of dicom file
    :param folder: source folder of dicom file
    :return: array of pixel data
    """
    path = Path(folder) / file
    # Get dicom file
    dicomfile = pydicom.dcmread(path)
    # Get pixel array
    image = dicomfile.pixel_array
    # Apply Modality LUT or Rescale Operation
    hu = apply_modality_lut(image, dicomfile)
    
    return hu


def check_dicom_lut_windowing(file, folder):
    """
    Function applies LUT Modality and VOI Modality functions.
    :param file: source dicom filename
    :param folder: source folder
    :return: numpy array
    """
    raise NotImplementedError("Needs to be checked")
    path = Path(folder) / file
    # Get dicom file
    dicomfile = pydicom.dcmread(path)
    # Get pixel array
    image = dicomfile.pixel_array
    # Apply Modality LUT or Rescale Operation
    hu = apply_modality_lut(image, dicomfile)
#     wd = pydicom.pixel_data_handlers.util.apply_voi_lut(hu, dicomfile)
#     wd = pydicom.pixel_data_handlers.util.apply_windowing(hu, dicomfile, index=0)
    width = dicomfile.WindowWidth
    center = dicomfile.WindowCenter
    lower_bound = int(center - width / 2)
    upper_bound = int(center + width / 2)
    array = hu
    array = np.where(array < lower_bound, lower_bound, array)
    array = np.where(array > upper_bound, upper_bound, array)
    
    return array


def get_ct_window_grayscale(array, width=1500, center=-600):
    """
    Functions calculates the upper and lower grey levels by given window parameters.
    Next it resales values in given array into grayscale.
    All values in array below lower level are set to black and above upper level are set to white.
    Values between levels are rescaled into 0-255 interval.
    https://radiopaedia.org/articles/windowing-ct
    :param array: array with values to rescale
    :param width: ct window width
    :param center: ct window center/level
    :return: array in gray scale values in specified ct window
    """
    # cut array to specified values range
    arr = cut_array_to_lung_window(array, width, center)
    # the lower grey level is calculated via WL - (WW ÷ 2)
    black = center - width / 2
    # the upper grey level is calculated via WL + (WW ÷ 2)
    white = center + width / 2
    arr = gray.convert_array_to_black_white_range(arr, black, white)

    return arr
