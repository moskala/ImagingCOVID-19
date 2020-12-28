import numpy as np
from skimage import measure
from scipy import interpolate
from PIL import Image, ImageDraw


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
    n_row = 3 * int(mask.shape[0] / 4)

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


def fill_contours(mask, min_length=0, smoothing=True):

    # Create an empty image to store the masked array
    mask_spline = np.ndarray(mask.shape, dtype=np.int8)
    mask_spline[:] = 0

    contours = measure.find_contours(mask, 0)

    if min_length > 0:
        contours = list(filter(lambda contour: len(contour[:, 1]) > min_length, contours))

    if smoothing:
        contours = list(map(lambda c: smooth_contours(c[:, 0], c[:, 1]), contours))
        for contour in contours:
            points = list(zip(contour[1], contour[0]))
            mask_spline = fill_polygon_points(mask_spline, points)
    else:
        for contour in contours:
            points = list(zip(contour[:, 1], contour[:, 0]))
            mask_spline = fill_polygon_points(mask_spline, points)
    # for contour in contours:
    #     mask_spline[np.round(contour[:, 0]).astype('int'), np.round(contour[:, 1]).astype('int')] = 1
    #     mask_spline = ndimage.binary_fill_holes(mask_spline)

    return mask_spline


def smooth_contours(x, y):
    tck, u = interpolate.splprep([x, y], s=0)
    out = interpolate.splev(u, tck)
    return out


def fill_polygon_points(img, points):
    image = Image.fromarray(img)
    ImageDraw.Draw(image).polygon(points, outline=1, fill=1)
    mask = np.array(image)
    # Zwórcić uwagę na obroty!
    return mask


# import matplotlib.pyplot as plt
#
# # Figura
# t = np.arange(0, 1.1, .1)
# xs = np.sin(2*np.pi*t)
# ys = np.cos(2*np.pi*t)
# xy = list(zip(xs*200+400, ys*200+250))
# rog = list(zip(xs*200+400, ys*200+250))
#
# img1 = np.zeros((512, 400))
# mask1 = fill_polygon_points(img1, xy)
# new_mask = fill_contours(mask1, smoothing=False)
#
# fig, (ax1, ax2) = plt.subplots(1, 2, figsize=[10, 5])
# ax1.imshow(mask1)
# ax2.imshow(new_mask)
# plt.show()