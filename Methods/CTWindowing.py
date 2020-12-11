"""
Module for checking in which computer tomography window  array values are
https://www.radiologycafe.com/medical-students/radiology-basics/ct-overview
"""


from pathlib import Path
import numpy as np
from enum import Enum
import pydicom
from pydicom.pixel_data_handlers.util import apply_modality_lut


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
intervals = {
  CTWindow.GrayscaleWindow: (0, 255),
  CTWindow.SoftTissueWindow: (-125, 225),
  CTWindow.BoneWindow: (-700, 1300),
  CTWindow.LungWindow: (-1200, 800),
}


def check_array_window(array):
    """
    Function checks in which CT window array values are.
    :param array: 2-dim numpy array
    :return: type of CTWindow which correspond with array values or None if no match is found
    """
    min_val = np.min(array)
    max_val = np.max(array)
    w = None
    
    # Function goes from the smallest interval
    for window in intervals:
        lower_bound, upper_bound = intervals[window]
        if (min_val >= lower_bound) & (max_val <= upper_bound):
            w = window
            break
        
    return w     


def cut_to_lung_window(array):
    """
    Function cuts values outside specified LungWindow interval.
    :param array: numpy array representing pixel array
    :return: numpy array which has values are subset of LungWindow interval
    """
    lower_bound, upper_bound = intervals[CTWindow.LungWindow]
    
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
    ct_window = check_array_window(array)
    
    if ct_window is None or ct_window is CTWindow.BoneWindow:
        array = cut_to_lung_window(array)
        ct_window = check_array_window(array)
    return ct_window, array


def check_dicom_lut(file, folder):
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

