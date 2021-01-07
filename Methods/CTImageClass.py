from ImageClass import *

import LungSegmentation.LungSegmentation_MethodA_dicom as sgWatershed
import LungSegmentation.LungSegmentation_MethodB_dicom as sgBinary
import LungSegmentation.LungSegmentation_MethodKMeans_AllTypes as sgKmeans


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
        gray_img = gray.get_grayscale_from_FileDataset(self.image_data)
        return sgKmeans.make_lungmask(gray_img, False)

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
        kmeans = self.get_segmented_lungs()
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
        gray_img = gray.convert_array_to_grayscale(self.get_current_slice())
        return sgKmeans.make_lungmask(gray_img, False)

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
        kmeans = self.get_segmented_lungs()
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
        return sgKmeans.make_lungmask(gray_img, False)

    def get_segmentation_figure(self):
        kmeans = self.get_segmented_lungs()
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
        return sgKmeans.make_lungmask(gray_img, False)

    def get_segmentation_figure(self):
        kmeans = self.get_segmented_lungs()
        figures = [self.get_current_slice(), kmeans]
        titles = ['Original image', 'KMeans segmentation']

        filename = sgUtils.get_segmentation_figure(figures, titles)

        return filename
