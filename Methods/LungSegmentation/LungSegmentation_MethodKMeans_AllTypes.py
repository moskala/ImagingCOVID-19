# źródło: https://www.raddq.com/dicom-processing-segmentation-visualization-in-python/

import numpy as np
import matplotlib.pyplot as plt
from skimage import morphology
from skimage import measure
from sklearn.cluster import KMeans
from pathlib import Path
import sys

sys.path.append(str(Path().resolve().parent))
import Grayscale as gray


def crop_mask_image(img, mask):

    labels = measure.label(mask)
    regions = measure.regionprops(labels)

    # Find boundries of regions
    min_row = (min(regions, key=lambda region: region.bbox[0])).bbox[0]
    min_col = (min(regions, key=lambda region: region.bbox[1])).bbox[1]
    max_row = (max(regions, key=lambda region: region.bbox[2])).bbox[2]
    max_col = (max(regions, key=lambda region: region.bbox[3])).bbox[3]

    # Crop images
    shift = 4
    crop_mask = mask[(min_row - shift):(max_row + shift), (min_col - shift):(max_col + shift)]
    crop_image = img[(min_row - shift):(max_row + shift), (min_col - shift):(max_col + shift)]

    return crop_image, crop_mask


def apply_convex_polygon(img, mask):
    labels = measure.label(mask)
    regions = measure.regionprops(labels)

    n_col = int(mask.shape[1] / 3)
    n_row = 2 * int(mask.shape[0] / 3)

    # Create an empty image to store the masked array
    mask_convex = mask.copy()

    for region in regions:
        convex = region.convex_image
        crop = region.image
        minr, minc, maxr, maxc = region.bbox
        crop[n_row:, 0:n_col] = (crop[n_row:, 0:n_col] == 1) | (convex[n_row:, 0:n_col] == 1)
        crop[n_row:, 2 * n_col:] = (crop[n_row:, 2 * n_col:] == 1) | (convex[n_row:, 2 * n_col:] == 1)
        mask_convex[minr:maxr, minc:maxc] = crop

    segmentation = mask_convex * img

    return segmentation, mask_convex


# Standardize the pixel values
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

>>>>>>> am/grayscale
    # Oryginal mask
    mask1 = morphology.dilation(mask, np.ones([10, 10]))  # one last dilation
    # Improved due to covid changes
    mask2 = morphology.area_closing(mask1, connectivity=2)

    # Cropped image and mask
    segmented, crop_mask = crop_mask_image(img, mask2)
    # Segmented image and final mask
    final_segment, final_mask = apply_convex_polygon(segmented, crop_mask)

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

# print("Przyklad jpg")
# image = gray.get_grayscale_from_jpg_png("covid5.jpg",
#                                         str(Path().resolve().parent.parent.parent / "images_data"))
# mask = make_lungmask(image, True)

# print("Przyklad dicom China")
# image = gray.get_grayscale_from_dicom("ser203img00109.dcm",
#                                       str(Path().resolve().parent.parent.parent / "images_data"))
# mask = make_lungmask(image, True)
>>>>>>> am/grayscale
