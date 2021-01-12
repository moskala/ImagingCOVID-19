from pathlib import Path

import nibabel
import numpy as np
from pydicom.pixel_data_handlers.util import apply_modality_lut
from enum import Enum

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Methods')))

import Grayscale as gray
import CTWindowing as ctwindow
import LungSegmentation.LungSegmentationUtilities as sgUtils
from SeverityScoringSystem import calculate_ratio_tts
import Anonymize.Anonymization as anonym


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
    __pixel_array = None
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
        raise NotImplementedError("Method should be overrided in derived classes.")

    def get_next_slice(self, value):
        """
        Method load next slice (for dicom or nifti images)
        and returns array containing pixel data for given slice.
        """
        pass

    def get_specific_size(self, value):
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

    def calculate_severity(self, regions):
        mask_infection = sgUtils.fill_selected_regions_on_mask(self.get_image_size(), regions)
        mask_infection = sgUtils.flip_mask_vertically(mask_infection)
        mask_lungs = self.get_segmented_lungs()
        ratio, tts = calculate_ratio_tts(mask_lungs, mask_infection)
        return ratio, tts

    def get_image_size(self):
        array = self.get_current_slice()
        height = array.shape[0]
        width = array.shape[1]
        return height, width

    def get_info(self):
        height, width = self.get_image_size()
        ct_window = self.get_ct_window()
        properties = {
            "Filename": self.src_filename,
            "File type": self.file_type,
            "Height": height,
            "Width": width,
            "CT Window Type": ct_window
        }

        return properties

    def get_image_to_draw(self):
        ct_window = self.get_ct_window()
        if ct_window is not None and ct_window == ctwindow.CTWindow.GrayscaleWindow:
            return self.get_current_grayscale_slice()
        else:
            return ctwindow.get_ct_window_grayscale(self.get_current_slice())

    def get_segmented_lungs(self):
        """
        Method makes lung segmentations.
        :return: numpy array with segmented area of lungs
        """
        raise NotImplementedError("Method should be overrided in derived classes.")

    def get_current_grayscale_slice(self):
        """
        Method returns grayscale array of current slice.
        :return: numpy array
        """
        raise NotImplementedError("Method should be overrided in derived classes.")

    def get_ct_window(self):
        raise NotImplementedError("Method should be overrided in derived classes.")

    def get_current_slice_number_to_show(self):
        return self.current_slice_number + 1

    def get_specific_slice(self, value=0):
        return self.__pixel_array


class DicomImage(ImageObject):
    """
    Class for representing dicom image object.
    """

    # List containing paths to all dicom images in source folder
    slices_path_list = []
    # Dicom Dataset
    image_data = None

    file_extensions = ["dcm", "DCM"]
    
    def __init__(self, folder, filename):
        
        super().__init__(folder, filename)
        self.file_type = ImageType.DCM
        self.image_data = anonym.get_anonymized_dicom(filename, folder)
        if self.image_data is None:
            raise TypeError("Error occurred during loading data.")
        # Set self.pixel_data to array in Hounsfield's units
        self.__pixel_array = self.get_hounsfield()
        # Get filenames of all dicom files in source folder
        self.slices_path_list = [elem for elem in Path(self.src_folder).iterdir()
                                 if elem.is_file() and elem.suffix[1:] in self.file_extensions]
        self.total_slice_number = len(self.slices_path_list)

    def get_current_slice(self):
        return self.__pixel_array

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
        self.__pixel_array = self.get_hounsfield()
        return self.__pixel_array
    
    def get_specific_slice(self, value):
        '''assuming value is not out of range'''
        self.current_slice_number = value
            
        self.src_filename = self.slices_path_list[value].name
        
        self.image_data = anonym.get_anonymized_dicom(self.src_filename, self.src_folder)
        self.__pixel_array = self.get_hounsfield()
        return self.__pixel_array

    def get_current_grayscale_slice(self):
        gray_img = gray.get_grayscale_from_FileDataset(self.image_data)
        return gray_img


class NiftiImage(ImageObject):
    """
    Class for representing nifti1 image object.
    """
    file_extensions = ["nii"]

    def __init__(self, folder, filename):
        
        super().__init__(folder, filename)
        self.file_type = ImageType.NIFTI

        self.image_data = anonym.get_anonymized_nifti(filename, folder)
        if self.image_data is None:
            raise TypeError("Error occurred during loading data.")
        self.__pixel_array = self.image_data.get_fdata().T
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
        return self.__pixel_array[self.current_slice_number]
    
    def get_next_slice(self, value):
        if value >= self.total_slice_number:
            self.current_slice_number = self.total_slice_number - 1
        elif value <= 0:
            self.current_slice_number = 0
        else:
            self.current_slice_number = value
            
        return self.__pixel_array[self.current_slice_number]

    def get_specific_slice(self, value):
        self.current_slice_number = value
            
        return self.__pixel_array[self.current_slice_number]

    def get_current_grayscale_slice(self):
        gray_img = gray.get_grayscale_from_nifti_slice(self.src_filename, self.src_folder, self.current_slice_number)
        return gray_img


class OneLayerImage(ImageObject):
    """
    Class for representing one layer image object.
    """

    def __init__(self, folder, filename):
        super().__init__(folder, filename)
        self.image_data = anonym.get_anonymized_png_jpg(filename, folder)
        if self.image_data is None:
            raise TypeError("Error occurred during loading data.")
        self.__pixel_array = np.array(self.image_data)
        self.total_slice_number = 1

    def get_current_slice(self):
        return self.__pixel_array

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

    def get_specific_slice(self, value):
        return self.get_current_slice()

    def get_current_grayscale_slice(self):
        gray_img = gray.get_grayscale_from_jpg_png(self.src_filename, self.src_folder)
        return gray_img

    def get_ct_window(self):
        return ctwindow.CTWindow.GrayscaleWindow


class JpgImage(OneLayerImage):
    """
    Class for representing jpg image object.
    """

    file_extensions = ["jpg", "jpeg", "JPG", "JPEG"]

    def __init__(self, folder, filename):
        
        super().__init__(folder, filename)
        self.file_type = ImageType.JPG


class PngImage(OneLayerImage):
    """
    Class for representing png image object.
    """

    file_extensions = ["png", "PNG"]

    def __init__(self, folder, filename):

        super().__init__(folder, filename)
        self.file_type = ImageType.PNG

