from LungSegmentationUtilities import fill_contours, crop_mask_image, compare_plots
import numpy as np
from skimage import morphology
from skimage import measure
from sklearn.cluster import KMeans
from pathlib import Path
import sys
sys.path.append(str(Path().resolve().parent))
import Grayscale as gray
import matplotlib.pyplot as plt
import scipy.ndimage
from scipy.ndimage.filters import gaussian_filter


def apply_convex_polygon(img, mask):
    labels = measure.label(mask)
    regions = measure.regionprops(labels)

    # n_col = int(mask.shape[1] / 3)
    # n_row = 3 * int(mask.shape[0] / 4)
    n_col = mask.shape[1]
    n_row = mask.shape[0]

    # Create an empty image to store the masked array
    mask_convex = mask.copy()

    for region in regions:
        convex = region.convex_image
        crop = region.image
        minr, minc, maxr, maxc = region.bbox
        # crop[n_row:,:] = (crop[n_row:, 0:n_col] == 1) | (convex[n_row:, 0:n_col] == 1)
        # crop[n_row:, 2 * n_col:] = (crop[n_row:, 2 * n_col:] == 1) | (convex[n_row:, 2 * n_col:] == 1)
        mask_convex[minr:maxr, minc:maxc] = crop | convex

    segmentation = mask_convex * img

    return segmentation, mask_convex


def make_lungmask(img):
    img_copy = img.copy()
    row_size = img.shape[0]
    col_size = img.shape[1]

    mean = np.mean(img_copy)
    std = np.std(img_copy)
    img_copy = img_copy - mean
    img_copy = img_copy / std

    # Find the average pixel value near the lungs
    # to renormalize washed out images
    middle = img_copy[int(col_size / 5):int(col_size / 5 * 2), int(row_size / 5 * 2):int(row_size / 5 * 4)]
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
    # threshold = np.mean(centers)
    threshold = np.min(centers)
    # threshold = mean
    thresh_img = np.where(img_copy < threshold, 1.0, 0.0)  # threshold the image
    # plt.imshow(thresh_img)

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
    # chosen_regions = good_regions[0:2]
    chosen_regions = good_regions

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
    filled_mask = fill_contours(crop_mask, min_length=100, smoothing=True)
    final_mask = gaussian_filter(filled_mask, .5)
    final_segment = final_mask * crop_img

    convex_img, convex_mask = apply_convex_polygon(crop_img, final_mask)

    kmeans = KMeans(n_clusters=5).fit(np.reshape(convex_img, [np.prod(convex_img.shape), 1]))
    centers = sorted(kmeans.cluster_centers_.flatten())
    # threshold = np.mean(centers)
    threshold = np.max(centers)
    # threshold = list(centers)[-2]
    thresh_img = np.where(convex_img < threshold, 1.0, 0.0)
    mask = thresh_img*convex_mask

    # plt.imshow(thresh_img*convex_img)
    eroded = morphology.erosion(mask, np.ones([3, 3]))
    # # plt.imshow(eroded)
    filled_mask = fill_contours(eroded, min_length=100, smoothing=True)
    # # plt.imshow(filled_mask)
    final_mask = gaussian_filter(filled_mask, .5)
    plt.imshow(final_mask*convex_img)
    # # plt.imshow(filled_mask)

    return final_segment



# Testy
import os
folder_name = r"D:\Studia\sem7\inzynierka\data\COVID-19 Radiography Database"
covid_folder = Path(folder_name) / "COVID-19"
normal_folder = Path(folder_name) / "NORMAL"

covid = os.listdir(covid_folder)
normal = os.listdir(normal_folder)
img = gray.get_grayscale_from_jpg_png(covid[0], str(covid_folder))
mask = make_lungmask(img)
compare_plots(img, mask)


