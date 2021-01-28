import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ImageMedical.ImageClass import *

import LungSegmentation.MethodWatershed as sgWatershed
import LungSegmentation.MethodBinary as sgBinary
import LungSegmentation.MethodKMeans as sgKmeans
from LungSegmentation.LungSegmentationUtilities import crop_mask_image


class CTDicomImage(DicomImage):

    def __init__(self, folder, filename):
        super().__init__(folder, filename)
        self.ct_window = self.check_ct_window()

    def check_ct_window(self):
        ct_window, min_val, max_val = ctwindow.check_array_window(self.get_current_slice())
        return ct_window

    def get_ct_window(self):
        return self.ct_window

    def get_segmented_lungs(self):

        if self.ct_window is ctwindow.CTWindow.GrayscaleWindow:
            gray_img = self.get_current_grayscale_slice()
            segment, mask = sgKmeans.make_lungmask(gray_img, crop=False)
            crop_segment, crop_mask = crop_mask_image(segment, mask)
            return crop_segment
        else:
            gray_img = self.get_current_grayscale_slice()
            segment, mask = sgKmeans.make_lungmask(gray_img, crop=False)
            img = self.get_current_slice()
            segmented_hu = np.where(mask == 1, img, -2000 * np.ones((len(img), len(img[0]))))
            center, width = ctwindow.get_window_interval(ctwindow.CTWindow.LungWindow)
            crop_segment, crop_mask = crop_mask_image(segmented_hu, mask)
            return ctwindow.get_ct_window_grayscale(crop_segment, width=width, center=center)

    def get_segmented_lungs_kmeans(self):
        gray_img = self.get_current_grayscale_slice()
        segment, mask = sgKmeans.make_lungmask(gray_img, crop=False)
        if self.ct_window is ctwindow.CTWindow.GrayscaleWindow:
            return segment
        else:
            img = self.get_current_slice()
            segmented = np.where(mask == 1, img, -2000 * np.ones((len(img), len(img[0]))))
            return segmented

    def get_segmented_lungs_watershed(self):
        """This function runs watershed segmentation"""
        try:
            segmented, mask = sgWatershed.seperate_lungs_and_mask(self.get_current_slice())
            return segmented
        except Exception as ex:
            print(ex)

    def get_segmented_lungs_binary(self):
        """This function runs binary segmentation"""
        try:
            ct_scan = anonym.get_anonymized_dicom(self.src_filename, self.src_folder)
            segmented, mask = sgBinary.get_segmented_lungs_and_mask(ct_scan.pixel_array)
            hu = self.get_hounsfield()
            segmented = np.where(mask == 1, hu, -2000 * np.ones((len(hu), len(hu[0]))))
            return segmented
        except Exception as ex:
            print(ex)

    def get_segmentation_figure(self):
        ct_window = self.check_ct_window()
        kmeans = self.get_segmented_lungs_kmeans()
        figures = [self.get_current_slice(), kmeans]
        titles = ['Original image', 'KMeans segmentation']

        if ct_window is not None and ct_window != ctwindow.CTWindow.GrayscaleWindow:
            binary = self.get_segmented_lungs_binary()
            water = self.get_segmented_lungs_watershed()
            figures.append(binary)
            titles.append('Binary segmentation')
            figures.append(water)
            titles.append('Watershed segmentation')

        filename = sgUtils.get_segmentation_figure(figures, titles)

        return filename


class CTNiftiImage(NiftiImage):

    def __init__(self, folder, filename):
        super().__init__(folder, filename)
        self.ct_window = self.check_ct_window()

    def get_ct_window(self):
        return self.ct_window

    def check_ct_window(self):
        ct_window, min_val, max_val = ctwindow.check_array_window(self.get_current_slice())
        return ct_window

    def get_segmented_lungs(self):

        if self.ct_window is ctwindow.CTWindow.GrayscaleWindow:
            gray_img = self.get_current_grayscale_slice()
            segment, mask = sgKmeans.make_lungmask(gray_img, crop=False)
            crop_segment, crop_mask = crop_mask_image(segment, mask)
            return crop_segment
        else:
            gray_img = self.get_current_grayscale_slice()
            segment, mask = sgKmeans.make_lungmask(gray_img, crop=False)
            img = self.get_current_slice()
            segmented_hu = np.where(mask == 1, img, -2000 * np.ones((len(img), len(img[0]))))
            center, width = ctwindow.get_window_interval(ctwindow.CTWindow.LungWindow)
            crop_segment, crop_mask = crop_mask_image(segmented_hu, mask)
            return ctwindow.get_ct_window_grayscale(crop_segment, width=width, center=center)

    def get_segmented_lungs_kmeans(self):
        gray_img = self.get_current_grayscale_slice()
        segment, mask = sgKmeans.make_lungmask(gray_img, crop=False)
        if self.ct_window is ctwindow.CTWindow.GrayscaleWindow:
            return segment
        else:
            img = self.get_current_slice()
            segmented = np.where(mask == 1, img, -2000 * np.ones((len(img), len(img[0]))))
            return segmented

    def get_segmented_lungs_watershed(self):
        """This function runs watershed segmentation"""
        try:
            segmented, mask = sgWatershed.seperate_lungs_and_mask(self.get_current_slice())
            return segmented
        except Exception as ex:
            print(ex)

    def get_segmented_lungs_binary(self):
        """This function runs binary segmentation"""
        try:
            ct_scan = self.get_current_slice()
            segmented, mask = sgBinary.get_segmented_lungs_and_mask(ct_scan, threshold=-400)
            segmented = np.where(mask == 1, ct_scan, -2000 * np.ones((len(ct_scan), len(ct_scan[0]))))
            return segmented
        except Exception as ex:
            print(ex)

    def get_segmentation_figure(self):
        ct_window = self.check_ct_window()
        kmeans = self.get_segmented_lungs_kmeans()
        figures = [self.get_current_slice(), kmeans]
        titles = ['Original image', 'KMeans segmentation']

        if ct_window is not None and ct_window != ctwindow.CTWindow.GrayscaleWindow:
            binary = self.get_segmented_lungs_binary()
            water = self.get_segmented_lungs_watershed()
            figures.append(binary)
            titles.append('Binary segmentation')
            figures.append(water)
            titles.append('Watershed segmentation')

        filename = sgUtils.get_segmentation_figure(figures, titles)

        return filename


class CTJpgImage(JpgImage):
    """
    Class for representing jpg image object.
    """

    def __init__(self, folder, filename):
        super().__init__(folder, filename)
        self.ct_window = ctwindow.CTWindow.GrayscaleWindow

    def get_ct_window(self):
        return self.ct_window

    def get_segmented_lungs(self):
        gray_img = gray.get_grayscale_from_jpg_png(self.src_filename, self.src_folder)
        segment, mask = sgKmeans.make_lungmask(gray_img, crop=True)
        return segment

    def get_segmented_lungs_kmeans(self):
        gray_img = self.get_current_grayscale_slice()
        segment, mask = sgKmeans.make_lungmask(gray_img, crop=False)
        return segment

    def get_segmentation_figure(self):
        kmeans = self.get_segmented_lungs_kmeans()
        figures = [self.get_current_slice(), kmeans]
        titles = ['Original image', 'KMeans segmentation']

        filename = sgUtils.get_segmentation_figure(figures, titles)

        return filename


class CTPngImage(PngImage):
    """
    Class for representing png image object.
    """

    def __init__(self, folder, filename):
        super().__init__(folder, filename)
        self.ct_window = ctwindow.CTWindow.GrayscaleWindow

    def get_ct_window(self):
        return self.ct_window

    def get_segmented_lungs(self):
        gray_img = gray.get_grayscale_from_jpg_png(self.src_filename, self.src_folder)
        segment, mask = sgKmeans.make_lungmask(gray_img, crop=True)
        return segment

    def get_segmented_lungs_kmeans(self):
        gray_img = self.get_current_grayscale_slice()
        segment, mask = sgKmeans.make_lungmask(gray_img, crop=False)
        return segment

    def get_segmentation_figure(self):
        kmeans = self.get_segmented_lungs_kmeans()
        figures = [self.get_current_slice(), kmeans]
        titles = ['Original image', 'KMeans segmentation']

        filename = sgUtils.get_segmentation_figure(figures, titles)

        return filename
