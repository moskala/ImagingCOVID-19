import numpy as np
from skimage import measure
from scipy import interpolate
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
# TODO comments

def crop_mask_image(img, mask):

    labels = measure.label(mask)
    regions = measure.regionprops(labels)
    if len(regions) == 0:
        return img, mask
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
    if len(x) >= 4:
        tck, u = interpolate.splprep([x, y], s=0)
        out = interpolate.splev(u, tck)
    else:
        out = [x, y]
    return out


def fill_polygon_points(img, points):
    image = Image.fromarray(img)
    ImageDraw.Draw(image).polygon(points, outline=1, fill=1)
    mask = np.array(image)
    # Zwórcić uwagę na obroty!
    return mask


def fill_selected_regions_on_mask(image_size, regions_points):
    # Check dimension of image
    if len(image_size) != 2:
        raise ValueError("Image size should have 2 dim but has {0}".format(len(image_size)))
    # Create empty mask
    mask = np.zeros(image_size)
    # Fill mask with given regions, apply smoothing
    for pts in regions_points:
        temp = np.zeros(image_size)
        temp = fill_polygon_points(temp, pts)
        mask = (mask == 1) | (temp == 1)
    return mask


def flip_mask_vertically(mask):
    return np.flip(mask, 0)


def compare_plots(image1, image2):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=[10, 5])
    ax1.imshow(image1)
    ax2.imshow(image2)
    plt.show()


def draw_lines_on_image(gray_image, regions_points):
    img = Image.fromarray(gray_image)
    rgb_img = Image.new("RGB", img.size)
    rgb_img.paste(img)
    for points in regions_points:
        map_points = [(x, gray_image.shape[0]-y) for x, y in points]
        map_points.append(map_points[0])
        ImageDraw.Draw(rgb_img).line(map_points, fill='red', width=2)
    image = np.array(rgb_img)
    return image


def get_segmentation_figure(figures, titles):

    if len(figures) < 2:
        raise ValueError("Too few figures.")

    if len(figures) == 4:
        fig2 = figures[2]
        fig3 = figures[3]
        val_min = min(np.min(fig2), np.min(fig3))
        val_max = max(np.max(fig2), np.max(fig3))

        fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2)
        ax2.imshow(fig2, cmap='gray', vmin=val_min, vmax=val_max)
        ax3.imshow(fig3, cmap='gray', vmin=val_min, vmax=val_max)

        ax2.set_title(titles[2])
        ax3.set_title(titles[3])

        ax2.axis('off')
        ax3.axis('off')
    else:
        fig, (ax0, ax1) = plt.subplots(1, 2)

    ax0.imshow(figures[0], cmap='gray')
    ax1.imshow(figures[1], cmap='gray')

    ax0.axis('off')
    ax1.axis('off')

    ax0.set_title(titles[0])
    ax1.set_title(titles[1])

    filename = "temp_mask_figure.jpg"
    fig.savefig(filename)

    return filename



# import matplotlib.pyplot as plt
#
# # Figura
# t = np.arange(0, 1.1, .1)
# xs = np.sin(2*np.pi*t)
# ys = np.cos(2*np.pi*t)
# xy = list(zip(xs*100+200, ys*100+200))
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
# img = Image.open("..\..\GUI\sample_image.jpg")
# rgbimg = Image.new("RGB", img.size)
# rgbimg.paste(img)
# arr = np.array(rgbimg)
# width = arr.shape[1]
# height = arr.shape[0]
# array = arr.reshape((height, width, 3))
# img = Image.fromarray(array, mode='RGB')
# contours = draw_lines_on_image(np.array(img), [xy])
# plt.imshow(contours)
# plt.show()

# im = Image.fromarray(arr, "RGB")
