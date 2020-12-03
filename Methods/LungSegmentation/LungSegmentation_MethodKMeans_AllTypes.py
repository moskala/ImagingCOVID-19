# źródło: https://www.raddq.com/dicom-processing-segmentation-visualization-in-python/

import numpy as np
# import pydicom
# import os
import matplotlib.pyplot as plt
# from glob import glob
# from mpl_toolkits.mplot3d.art3d import Poly3DCollection
# import scipy.ndimage
from skimage import morphology
from skimage import measure
# from skimage.transform import resize
from sklearn.cluster import KMeans
# from plotly import __version__
# from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
# from plotly.tools import FigureFactory as FF
# from plotly.graph_objs import *
#
# import PixelArrays
from pathlib import Path
import pylibjpeg
import sys

sys.path.append(str(Path().resolve().parent))
import Grayscale as gray
from ImageClass import *


def get_m_horizontal(array):
    mn = 0
    mx=0
    for i in range(0,len(array)):
        if(not all(elem<=0 for elem in array[i])):
            mn = i
            break
    for i in range(0,len(array)):
        if(not all(elem<=0 for elem in array[len(array)-i-1])):
            mx = len(array)-i-1
            break
    return mn,mx


def plot_crop(array,origin):
    lst=[]
    n,x = get_m_horizontal(np.rot90(np.rot90(np.rot90(origin))))
    u,d = get_m_horizontal(origin)
    for i in range(u,d):
        lst.append(array[i][n:x])
    return np.array(lst)

# Standardize the pixel values
def make_lungmask(img, display=False):
    row_size = img.shape[0]
    col_size = img.shape[1]

    mean = np.mean(img)
    std = np.std(img)
    img = img - mean
    img = img / std
    # Find the average pixel value near the lungs
    # to renormalize washed out images
    middle = img[int(col_size / 5):int(col_size / 5 * 4), int(row_size / 5):int(row_size / 5 * 4)]
    mean = np.mean(middle)
    max = np.max(img)
    min = np.min(img)
    # To improve threshold finding, I'm moving the
    # underflow and overflow on the pixel spectrum
    img[img == max] = mean
    img[img == min] = mean
    #
    # Using Kmeans to separate foreground (soft tissue / bone) and background (lung/air)
    #
    kmeans = KMeans(n_clusters=2).fit(np.reshape(middle, [np.prod(middle.shape), 1]))
    centers = sorted(kmeans.cluster_centers_.flatten())
    threshold = np.mean(centers)
    thresh_img = np.where(img < threshold, 1.0, 0.0)  # threshold the image

    # First erode away the finer elements, then dilate to include some of the pixels surrounding the lung.
    # We don't want to accidentally clip the lung.

    eroded = morphology.erosion(thresh_img, np.ones([3, 3]))
    dilation = morphology.dilation(eroded, np.ones([8, 8]))

    labels = measure.label(dilation)  # Different labels are displayed in different colors
    label_vals = np.unique(labels)
    regions = measure.regionprops(labels)
    good_labels = []
    for prop in regions:
        B = prop.bbox
        # B = (min_row, min_col, max_row, max_col)
        if B[3] < col_size and B[2] < row_size and B[0] > 0 and B[1] > 0:
            good_labels.append(prop.label)
        # To było wcześniej:
    #         if B[2]-B[0]<row_size/10*9 and B[3]-B[1]<col_size/10*9 and B[0]>row_size/5 and B[2]<col_size/5*4:
    #             good_labels.append(prop.label)
    mask = np.ndarray([row_size, col_size], dtype=np.int8)
    mask[:] = 0
    #
    #  After just the lungs are left, we do another large dilation
    #  in order to fill in and out the lung mask
    #
    for N in good_labels:
        mask = mask + np.where(labels == N, 1, 0)
    # Oryginal mask
    mask1 = morphology.dilation(mask, np.ones([10, 10]))  # one last dilation
    # Improved due to covid changes
    mask2 = morphology.area_closing(mask1, connectivity=2)

    if (display):
        fig, ax = plt.subplots(4, 2, figsize=[12, 12])
        ax[0, 0].set_title("Original")
        ax[0, 0].imshow(img, cmap='gray')
        ax[0, 0].axis('off')
        ax[0, 1].set_title("Threshold")
        ax[0, 1].imshow(thresh_img, cmap='gray')
        ax[0, 1].axis('off')
        ax[1, 0].set_title("After Erosion and Dilation")
        ax[1, 0].imshow(dilation, cmap='gray')
        ax[1, 0].axis('off')
        ax[1, 1].set_title("Color Labels")
        ax[1, 1].imshow(labels)
        ax[1, 1].axis('off')
        ax[2, 0].set_title("Final Mask")
        ax[2, 0].imshow(mask, cmap='gray')
        ax[2, 0].axis('off')
        ax[2, 1].set_title("Apply Mask on Original")
        ax[2, 1].imshow(mask1 * img, cmap='gray')
        ax[2, 1].axis('off')
        ax[3, 0].set_title("Final second Mask")
        ax[3, 0].imshow(mask2, cmap='gray')
        ax[3, 0].axis('off')
        ax[3, 1].set_title("Apply Mask on Original")
        ax[3, 1].imshow(mask2 * img, cmap='gray')
        ax[3, 1].axis('off')

        plt.show()

    # szybka konwersja na 
    ret = mask2 * img
    # print(mask.flatten()[0])
    # mn = np.minimum(mask.flatten())
    # ret = np.where(mask==mask.flatten()[0], mn , ret)
    # plt.imshow(ret,cmap='gray')
    # plt.show()
    ret = plot_crop(ret,ret)
    ret = gray.convert_array_to_grayscale(ret)
    return np.where(ret==ret.flatten()[0], 0 , ret)

# Przykładowe wywołania
# print("Przyklad dicom Italy")
# image = gray.get_grayscale_from_dicom("Italy_case010073.dcm", r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\wloch1")
# image = gray.get_grayscale_from_dicom("ser204img00070.dcm", r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\chin")
image = gray.get_grayscale_from_dicom("1-070.dcm", r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\zdrowy2\11-24-2003-RTRCCTTHORAX8FHighCONTRAST Adult-11396\0.000000-CTRespCT  3.0  B30f  50 Ex-14473")
#dcm = DicomImage(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\chin",r"ser204img00070.dcm")
mask = make_lungmask(image)
plt.imshow(mask,cmap='gray')
plt.show()