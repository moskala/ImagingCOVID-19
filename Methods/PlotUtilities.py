import nibabel
import matplotlib.pyplot as plt
import pydicom
import matplotlib.image as mpimg
from pathlib import Path


def show_dicom(file_path):
    dcm = pydicom.dcmread(file_path)

    plt.axis('off')
    plt.imshow(dcm.pixel_array, cmap='gray')
    plt.show()


def show_nii(file_path, value):
    ct = nibabel.load(file_path)
    ct_array = ct.get_fdata()
    ct_array = ct_array.T

    if value < 0:
        value = 0
    elif value >= len(ct_array):
        value = len(ct_array) - 1

    plt.axis('off')
    plt.imshow(ct_array[value], cmap='gray')
    plt.show()


def show_jpg_png(file_path):
    img = mpimg.imread(file_path)

    plt.axis('off')
    plt.imshow(img)
    plt.show()


# Przykłady:
# show_dicom(r"D:\Studia\sem7\inzynierka\data\covidctscans_org\16_Italy\Original Dicom\Italy_case010000.dcm")
# show_nii(r"D:\Studia\sem7\inzynierka\data\segmentation\ct_scan\coronacases_org_001.nii", 5)
# show_jpg_png(r'D:\Studia\sem7\inzynierka\data\test\test\0.jpg')
# show_jpg_png(r'D:\Studia\sem7\inzynierka\data\test\test\2237.png')

def get_plot_data_dicom(file_path):
    return pydicom.dcmread(file_path).pixel_array


def get_plot_data_dicom_all(folder_path):
    array = []
    for file in Path(folder_path).iterdir():
        array.append(pydicom.dcmread(file).pixel_array)
    return array


def get_plot_data_nii(file_path, value):

    ct = nibabel.load(file_path)
    ct_array = ct.get_fdata()
    ct_array = ct_array.T

    if value < 0:
        value = 0
    elif value >= len(ct_array):
        value = len(ct_array) - 1

    return ct_array[value]

def get_plot_data_nii_all(file_path):

    ct = nibabel.load(file_path)
    ct_array = ct.get_fdata()
    ct_array = ct_array.T

    return ct_array


def get_plot_data_jpg_png(file_path):
    return mpimg.imread(file_path)

