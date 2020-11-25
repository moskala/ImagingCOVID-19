# zrodlo: https://www.kaggle.com/zstarosolski/lung-segmentation

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import skimage, os
from skimage.morphology import ball, disk, dilation, binary_erosion, remove_small_objects, erosion, closing, reconstruction, binary_closing
from skimage.measure import label,regionprops, perimeter
from skimage.filters import roberts, sobel
from skimage import measure, feature
from skimage.segmentation import clear_border
from skimage import data
from scipy import ndimage as ndi
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import pydicom
import scipy.misc
import numpy as np
import pylibjpeg

class SegmentationB:
    @staticmethod
    def read_ct_scan(folder_name):
        # Read the slices from the dicom file
        slices = [pydicom.dcmread(os.path.join(folder_name,filename)) for filename in os.listdir(folder_name)]
        
        # Sort the dicom slices in their respective order
        slices.sort(key=lambda x: int(x.InstanceNumber))
        
        # Get the pixel values for all the slices
        slices = np.stack([s.pixel_array for s in slices])
        slices[slices == -2000] = 0
        return slices
        
    @staticmethod
    def get12_range(array):
        return 0.5*abs(max(array.flatten())-min(array.flatten()))
    @staticmethod
    def get_segmented_lungs(im):
        '''
        This funtion segments the lungs from the given 2D slice.
        '''
        # Convert into a binary image. 
        binary = im < SegmentationB.get12_range(im)
        # plt.imshow(binary, cmap=plt.cm.gray)
        
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
        
        return im

    # @staticmethod
    # def plot_ct_scan(scan,val):
    #     f, plots = plt.subplots(int(scan.shape[0] / 20) + 1, 4, sharex='col', sharey='row', figsize=(50, 50))
    #     for i in range(0, scan.shape[0], 5):
    #         plots[int(i / 20), int((i % 20) / 5)].axis('off')
    #         plots[int(i / 20), int((i % 20) / 5)].imshow(scan[i], cmap=plt.cm.bone) 

                
    @staticmethod
    def segment_lung_from_ct_scan(ct_scan,val):
        return np.asarray(SegmentationB.get_segmented_lungs(ct_scan[val]))

    @staticmethod
    def segment_lung_from_ct_scan_all(ct_scan):
        return np.asarray([SegmentationB.get_segmented_lungs(slice) for slice in ct_scan])