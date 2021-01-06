from pathlib import Path

import Anonymize.Anonymization as anonym
import PixelArrays
import pydicom
import nibabel
import numpy as np
import matplotlib.pyplot as plt
from pydicom.pixel_data_handlers.util import apply_modality_lut

from PIL import Image  
from enum import Enum
import CTWindowing as window
import Grayscale as gray
import LungSegmentation.LungSegmentation_MethodKMeans_AllTypes as sgKmeans
import LungSegmentation.LungSegmentation_MethodB_dicom as sgBinary
import LungSegmentation.LungSegmentation_MethodA_dicom as sgWatershed



class ImageType(Enum):
    """
    Enum type for representing image format.
    """
    DCM = 0
    NIFTI = 1
    JPG = 2
    PNG = 3

    def __str__(self):
        return self.name


class ImageObject(object):
    """
    Base class for representing image object and performing methods dedicated for every image type.
    """
    # Path to source folder which stores file
    src_folder = None
    # Filename with extension
    src_filename = None

    # Type of image file specified by enum ImageType
    file_type = None

    # Numpy array of pixel data for image
    pixel_array = None
    # Number of current layer of image
    current_slice_number = 0
    # Possible file extenstions for given file format
    file_extensions = None
    
    def __init__(self, src_folder, filename):
        
        self.src_folder = src_folder
        self.src_filename = filename
        self.current_slice_number = 0
        self.total_slice_number = 0
    
    def save_anonymized_file(self, filename, destination_folder):
        """ Method saves current image to destination_folder as filename. """
        raise NotImplementedError("Method should be overrided in derived classes.")

    def get_current_slice(self):
        """ Method returns array containing pixel data for current image. """
        return self.pixel_array

    def get_next_slice(self, value):
        """
        Method load next slice (for dicom or nifti images)
        and returns array containing pixel data for given slice.
        """
        pass

    def get_specific_size(self,value):
        """
        Method load specific slice (for dicom or nifti images)
        and returns array containing pixel data for given slice.
        """
        pass

    def get_file_path(self):
        """
        Methods returns path to image file as string.
        """
        return str(Path(self.src_folder) / self.src_filename)

    def get_filename_with_extension(self, filename: str):
        """
        Method check if given filename has correct file extensions.
        If filename has no extension, default extension for this file type will be added.
        If filename has incorrect extension, exception will be thrown.
        :param filename: string representing name of file
        :return: filename or filename with added extenstion
        """
        splitted = filename.split(".")
        if len(splitted) == 1:
            # filename has no extension, so it is added
            filename = filename + "." + self.file_extensions[0]
        elif splitted[-1] not in self.file_extensions:
            # extension is not correct
            raise TypeError("Wrong file extension: expected {0} but was{1}.".format(self.file_extenstions, splitted[-1]))

        return filename

    def check_ct_window(self):
        ct_window, min_val, max_val = window.check_array_window(self.get_current_slice())
        return ct_window

    def get_info(self):
        array = self.get_current_slice()
        height = array.shape[0]
        width = array.shape[0]
        ct_window = self.check_ct_window()
        properties = {
            "Filename": self.src_filename,
            "File type": self.file_type,
            "Height": height,
            "Width": width,
            "CT Window Type": ct_window
        }

        return properties

    def get_segmented_lungs(self):
        """
        Method makes lung segmentations.
        :return: numpy array with segmented area of lungs
        """
        raise NotImplementedError("Method should be overrided in derived classes.")

    def get_size(self):
        """
        Method gets 2-dim size of image
        :return: image height, image width
        """
        arr = self.get_current_slice()
        return arr[0], arr[1]

    def get_current_grayscale_slice(self):
        """
        Method returns grayscale array of current slice.
        :return: numpy array
        """
        raise NotImplementedError("Method should be overrided in derived classes.")

    def get_segmentation_figure(self):
        fig, (ax0, ax1) = plt.subplots(1, 2)
        ax0.imshow(self.get_current_slice(), cmap='gray')
        ax1.imshow(self.get_segmented_lungs(), cmap='gray')
        ax0.axis('off')
        ax1.axis('off')
        ax0.set_title('Original image')
        ax1.set_title('KMeans segmentation')
        filename = "temp_mask.jpg"
        fig.savefig(filename)

        return filename


class DicomImage(ImageObject):
    """
    Class for representing dicom image object.
    """

    # List containing paths to all dicom images in source folder
    slices_path_list = []
    # Dicom Dataset
    image_data = None
    
    def __init__(self, folder, filename):
        
        super().__init__(folder, filename)
        self.file_type = ImageType.DCM
        self.file_extensions = ["dcm", "DCM"]
        self.image_data = anonym.get_anonymized_dicom(filename, folder)
        if self.image_data is None:
            raise TypeError("Error occurred during loading data.")
        # Set self.pixel_data to array in Hounsfield's units
        self.pixel_array = self.get_hounsfield()
        # Get filenames of all dicom files in source folder
        self.slices_path_list = [elem for elem in Path(self.src_folder).iterdir()
                                 if elem.is_file() and elem.suffix[1:] in self.file_extensions]
        self.total_slice_number = len(self.slices_path_list)

    def save_anonymized_file(self, filename, destination_folder):
        try:
            filename = self.get_filename_with_extension(filename)
            output_file_path = Path(destination_folder) / filename
            self.image_data.save_as(output_file_path)
            return True
        
        except Exception as ex:
            print(ex)
            return False

    def get_hounsfield(self):
        hu = apply_modality_lut(self.image_data.pixel_array, self.image_data)
        return hu
    
    def get_next_slice(self, value):
        
        if value >= self.total_slice_number:
            self.current_slice_number = self.total_slice_number - 1
        elif value <= 0:
            self.current_slice_number = 0
        else:
            self.current_slice_number = value
            
        self.src_filename = self.slices_path_list[value].name
        
        self.image_data = anonym.get_anonymized_dicom(self.src_filename, self.src_folder)
        self.pixel_array = self.get_hounsfield()
        return self.pixel_array
    
    def get_specific_slice(self, value):
        '''assuming value is not out of range'''
        self.current_slice_number = value
            
        self.src_filename = self.slices_path_list[value].name
        
        self.image_data = anonym.get_anonymized_dicom(self.src_filename, self.src_folder)
        self.pixel_array = self.get_hounsfield()
        return self.pixel_array

    def check_ct_window(self):
        ct_window, array = window.check_array_window_or_cut(self.get_current_slice())
        return ct_window

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

    def get_current_grayscale_slice(self):
        gray_img = gray.get_grayscale_from_FileDataset(self.image_data)
        return gray_img

    def get_segmentation_figure(self):
        ct_window = self.check_ct_window()
        kmeans = self.get_segmented_lungs()
        if ct_window is not None and ct_window != window.CTWindow.GrayscaleWindow:
            binary = self.get_segmented_lungs_binary()
            water = self.get_segmented_lungs_watershed()
            val_min = min(np.min(binary), np.min(water))
            val_max = max(np.max(binary), np.max(water))

            fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2)
            ax2.imshow(binary, cmap='gray', vmin=val_min, vmax=val_max)
            ax3.imshow(water, cmap='gray', vmin=val_min, vmax=val_max)

            ax2.set_title('Binary segmentation')
            ax3.set_title('Watershed segmentation')

            ax2.axis('off')
            ax3.axis('off')
        else:
            fig, (ax0, ax1) = plt.subplots(1, 2)

        ax0.imshow(self.get_current_slice(), cmap='gray')
        ax1.imshow(kmeans, cmap='gray', vmin=0, vmax=255)

        ax0.axis('off')
        ax1.axis('off')

        ax0.set_title('Original image')
        ax1.set_title('KMeans segmentation')

        filename = "temp_mask.jpg"
        fig.savefig(filename)

        return filename


class NiftiImage(ImageObject):
    """
    Class for representing nifti1 image object.
    """

    def __init__(self, folder, filename):
        
        super().__init__(folder, filename)
        self.file_type = ImageType.NIFTI
        self.file_extensions = ["nii"]

        self.image_data = anonym.get_anonymized_nifti(filename, folder)
        if self.image_data is None:
            raise TypeError("Error occurred during loading data.")
        self.pixel_array = self.image_data.get_fdata().T
        self.total_slice_number = self.image_data.shape[2]

    def save_anonymized_file(self, filename, destination_folder):
        
        try:
            filename = self.get_filename_with_extension(filename)
            output_file_path = Path(destination_folder) / filename
            nibabel.save(self.image_data, output_file_path)
            return True
        
        except Exception as ex:
            print(ex)
            return False
    
    def get_current_slice(self):
        return self.pixel_array[self.current_slice_number]
    
    def get_next_slice(self, value):
        if value >= self.total_slice_number:
            self.current_slice_number = self.total_slice_number - 1
        elif value <= 0:
            self.current_slice_number = 0
        else:
            self.current_slice_number = value
            
        return self.pixel_array[self.current_slice_number]

    def get_specific_slice(self, value):
        self.current_slice_number = value
            
        return self.pixel_array[self.current_slice_number]

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

    def check_ct_window(self):
        ct_window = window.check_array_window(self.get_current_slice())
        return ct_window

    def get_segmentation_figure(self):
        ct_window = self.check_ct_window()
        kmeans = self.get_segmented_lungs()
        if ct_window is not None and ct_window != window.CTWindow.GrayscaleWindow:
            water = self.get_segmented_lungs_watershed()

            fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2)
            ax2.imshow(water, cmap='gray')
            ax2.set_title('Watershed segmentation')
            ax2.axis('off')
            ax3.axis('off')
        else:
            fig, (ax0, ax1) = plt.subplots(1, 2)

        ax0.imshow(self.get_current_slice(), cmap='gray')
        ax1.imshow(kmeans, cmap='gray', vmin=0, vmax=255)

        ax0.axis('off')
        ax1.axis('off')

        ax0.set_title('Original image')
        ax1.set_title('KMeans segmentation')

        filename = "temp_mask.jpg"
        fig.savefig(filename)

        return filename

    def get_current_grayscale_slice(self):
        gray_img = gray.get_grayscale_from_nifti_slice(self.src_folder, self.src_filename)
        return gray_img

    def get_segmented_lungs_watershed(self):
        """This function runs watershed segmentation"""
        try:
            segmented, mask = sgWatershed.seperate_lungs_and_mask(self.get_current_slice())
            return segmented
        except Exception as ex:
            print(ex)

    def check_ct_window(self):
        ct_window, array = window.check_array_window_or_cut(self.get_current_slice())
        return ct_window


class OneLayerImage(ImageObject):
    """
    Class for representing one layer image object.
    """

    def __init__(self, folder, filename):
        super().__init__(folder, filename)
        self.image_data = anonym.get_anonymized_png_jpg(filename, folder)
        if self.image_data is None:
            raise TypeError("Error occurred during loading data.")
        self.pixel_array = np.array(self.image_data)
        self.total_slice_number = 1

    def save_anonymized_file(self, filename, destination_folder):

        try:
            filename = super().get_filename_with_extension(filename)
            output_file_path = Path(destination_folder) / filename
            self.image_data.save(output_file_path)
            return True

        except Exception as ex:
            print(ex)
            return False

    def get_next_slice(self, value):
        return self.get_current_slice()

    def get_segmented_lungs(self):
        gray_img = gray.get_grayscale_from_jpg_png(self.src_filename, self.src_folder)
        return sgKmeans.make_lungmask(gray_img, False)

    def get_current_grayscale_slice(self):
        gray_img = gray.get_grayscale_from_jpg_png(self.src_folder, self.src_filename)
        return gray_img

    def check_ct_window(self):
        return window.CTWindow.GrayscaleWindow


class JpgImage(OneLayerImage):
    """
    Class for representing jpg image object.
    """

    def __init__(self, folder, filename):
        
        super().__init__(folder, filename)
        self.file_type = ImageType.JPG
        self.file_extensions = ["jpg", "jpeg", "JPG", "JPEG"]
    

class PngImage(OneLayerImage):
    """
    Class for representing png image object.
    """

    def __init__(self, folder, filename):

        super().__init__(folder, filename)
        self.file_type = ImageType.PNG
        self.file_extensions = ["png", "PNG"]
