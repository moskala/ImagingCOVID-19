# zrodlo: https://www.kaggle.com/zstarosolski/lung-segmentation

import skimage
import os
from skimage.morphology import disk, binary_erosion, binary_closing
from skimage.measure import label, regionprops
from skimage.filters import roberts
from skimage.segmentation import clear_border
from scipy import ndimage as ndi
import pydicom
import numpy as np


class SegmentationB:
    @staticmethod
    def read_ct_scan(folder_name):
        """
        Function reads a folder of .dcm files to a list of FileDataset objects
        Then it extracts a numpy ndarray object called 'pixel_array' from each FileDataset
        and stacks them together

        :param folder_name: folder path
        :return: slices: a stack of pixel arrays
        """

        # Read the slices from the dicom file
        slices = [pydicom.dcmread(os.path.join(folder_name,filename)) for filename in os.listdir(folder_name)]
        
        # Sort the dicom slices in their respective order
        slices.sort(key=lambda x: int(x.InstanceNumber))
        
        # Get the pixel values for all the slices
        slices = np.stack([s.pixel_array for s in slices])
        slices[slices == -2000] = 0
        return slices

    @staticmethod
    def get_segmented_lungs(im, threshold=604):
        """
        This funtion segments the lungs from the given 2D slice in the form of numpy ndarray.

        :param threshold: threshold value
        :param im: numpy ndarray of a 2D slice
        :return: im: numpy ndarray of a 2D slice with segmented lungs
        """        
        # Convert into a binary image. 
        binary = im < threshold

        # Remove the blobs connected to the border of the image
        cleared = clear_border(binary)

        # Label the image
        label_image = label(cleared)

        # Keep the labels with 2 largest areas
        areas = [r.area for r in regionprops(label_image)]
        areas.sort()
        if len(areas) > 2:
            for region in regionprops(label_image):
                if region.area < areas[-2]:
                    for coordinates in region.coords:                
                        label_image[coordinates[0], coordinates[1]] = 0
        binary = label_image > 0

        # Closure operation with disk of radius 12
        selem = disk(2)
        binary = binary_erosion(binary, selem)
        
        selem = disk(10)
        binary = binary_closing(binary, selem)
        
        # Fill in the small holes inside the lungs
        edges = roberts(binary)
        binary = ndi.binary_fill_holes(edges)

        # Superimpose the mask on the input image
        get_high_vals = binary == 0
        im[get_high_vals] = 0

        # plt.imshow(binary)
        # plt.show()
        
        return im

    @staticmethod
    def segment_lung_from_ct_scan(ct_scan,val):
        """
        This funtion performs segmentation of the lungs, given the stack of slices and the index.

        :param ct_scan: a stack of numpy ndarrays
        :param val: an index of wanted 2D slice to be segmented
        :return: numpy ndarray of a 2D slice with segmented lungs
        """  
        return np.asarray(SegmentationB.get_segmented_lungs(ct_scan[val]))

    @staticmethod
    def segment_lung_from_ct_scan_all(ct_scan):
        """
        This funtion performs segmentation of the lungs for all slices in the given stack.

        :param ct_scan: a stack of numpy ndarrays
        :return: numpy ndarray of a 2D slices with segmented lungs
        """  
        return np.asarray([SegmentationB.get_segmented_lungs(slice) for slice in ct_scan])


def get_segmented_lungs_and_mask(image_array, threshold=604):
    """
    This funtion segments the lungs from the given 2D slice in the form of numpy ndarray.

    :param threshold: threshold value for binary image
    :param image_array: numpy ndarray of a 2D slice
    :return: im: numpy ndarray of a 2D slice with segmented lungs
    """
    # Convert into a binary image.
    binary = image_array < threshold

    # Remove the blobs connected to the border of the image
    cleared = clear_border(binary)

    # Label the image
    label_image = label(cleared)

    # Keep the labels with 2 largest areas
    areas = [r.area for r in regionprops(label_image)]
    areas.sort()
    if len(areas) > 2:
        for region in regionprops(label_image):
            if region.area < areas[-2]:
                for coordinates in region.coords:
                    label_image[coordinates[0], coordinates[1]] = 0
    binary = label_image > 0

    # Closure operation with disk of radius 12
    selem = disk(2)
    binary = binary_erosion(binary, selem)

    selem = disk(10)
    binary = binary_closing(binary, selem)

    # Fill in the small holes inside the lungs
    edges = roberts(binary)
    binary = ndi.binary_fill_holes(edges)

    segmented = np.where(binary == 1, image_array, -2000 * np.ones((len(image_array), len(image_array[0]))))
    return segmented, binary
