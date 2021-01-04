# źródło: https://www.raddq.com/dicom-processing-segmentation-visualization-in-python/

import numpy as np
import matplotlib.pyplot as plt
from skimage import morphology
from skimage import measure
from sklearn.cluster import KMeans
from pathlib import Path
import sys
import scipy.ndimage as ndimage

sys.path.append(str(Path().resolve().parent))
import Grayscale as gray
from LungSegmentation.LungSegmentationUtilities import *


def make_lungmask(img, display=False):
    img_copy = img.copy()
    row_size = img.shape[0]
    col_size = img.shape[1]

    mean = np.mean(img_copy)
    std = np.std(img_copy)
    img_copy = img_copy - mean
    img_copy = img_copy / std

    # Find the average pixel value near the lungs
    # to renormalize washed out images
    middle = img_copy[int(col_size / 5):int(col_size / 5 * 4), int(row_size / 5):int(row_size / 5 * 4)]
    mean = np.mean(middle)
    max_tone = np.max(img_copy)
    min_tone = np.min(img_copy)

    # To improve threshold finding, I'm moving the
    # underflow and overflow on the pixel spectrum
    img_copy[img_copy == max_tone] = mean
    img_copy[img_copy == min_tone] = mean

    # Using Kmeans to separate foreground (soft tissue / bone) and background (lung/air)
    kmeans = KMeans(n_clusters=2).fit(np.reshape(middle, [np.prod(middle.shape), 1]))
    centers = sorted(kmeans.cluster_centers_.flatten())
    threshold = np.mean(centers)
    thresh_img = np.where(img_copy < threshold, 1.0, 0.0)  # threshold the image

    # First erode away the finer elements, then dilate to include some of the pixels surrounding the lung.
    eroded = morphology.erosion(thresh_img, np.ones([3, 3]))
    dilation = morphology.dilation(eroded, np.ones([8, 8]))

    labels = measure.label(dilation)
    # Labeled input image. Labels with value 0 are ignored.
    regions = measure.regionprops(labels)
    good_labels = []

    good_regions = list(filter(lambda region:
                               region.bbox[3] < col_size and
                               region.bbox[2] < row_size and
                               region.bbox[0] > 0 and
                               region.bbox[1] > 0 and
                               region.area > 1000,
                               regions))
    good_regions = list(sorted(good_regions, key=lambda region: region.area, reverse=True))
    chosen_regions = good_regions[0:2]
    for reg in chosen_regions:
        good_labels.append(reg.label)

    mask = np.ndarray([row_size, col_size], dtype=np.int8)
    mask[:] = 0

    #  After just the lungs are left, we do another large dilation
    #  in order to fill in and out the lung mask
    for N in good_labels:
        mask = mask + np.where(labels == N, 1, 0)

    # Oryginal mask
    mask1 = morphology.dilation(mask, np.ones([10, 10]))  # one last dilation
    # Improved due to covid changes
    mask2 = morphology.area_closing(mask1, connectivity=2)

    # Cropped image and mask
    crop_img, crop_mask = crop_mask_image(img, mask2)
    # Find contours and fill mask
    filled_mask = fill_contours(crop_mask, min_length=100)
    # Find convex polygon and change mask
    # final_segment, final_mask = apply_convex_polygon(crop_img, filled_mask)
    # print("Original shape: {0} Cropped_shape: {1}".format(img.shape, final_segment.shape))
    final_mask = filled_mask
    final_segment = final_mask*crop_img
    if display:
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4)
        ax1.set_title("Original")
        ax1.imshow(img, cmap='gray')
        ax1.axis('off')

        ax2.set_title("Threshold")
        ax2.imshow(thresh_img, cmap='gray')
        ax2.axis('off')

        ax3.set_title("Mask")
        ax3.imshow(final_mask, cmap='gray')
        ax3.axis('off')

        ax4.set_title("Segmentation")
        ax4.imshow(final_segment, cmap='gray')
        ax4.axis('off')

        plt.show()

    return final_segment


# Przykładowe wywołania z rysowaniem
# print("Przyklad dicom Italy")
# image = gray.get_grayscale_from_dicom("Italy_case010060.dcm",
#                                       str(Path().resolve().parent.parent.parent / "images_data" / "pacjent_dcm" ))
# mask = make_lungmask(image, True)
#
# print("Przyklad jpg")
# image = gray.get_grayscale_from_jpg_png("covid5.jpg",
#                                         str(Path().resolve().parent.parent.parent / "images_data"))
# mask = make_lungmask(image, True)
#
# print("Przyklad dicom China")
# image = gray.get_grayscale_from_dicom("ser203img00109.dcm",
#                                       str(Path().resolve().parent.parent.parent / "images_data"))
# mask = make_lungmask(image, True)

