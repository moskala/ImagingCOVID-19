from pathlib import Path

import Anonymize.Anonymization as anonym
import PixelArrays
import pydicom
import nibabel
import numpy as np

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
    # Image object depending on image type
    image_object = None
    # Possible file extenstions for given file format
    # file_extensions = []
    
    def __init__(self, src_folder, filename):
        
        self.src_folder = src_folder
        self.src_filename = filename
        self.current_slice_number = 0
        self.total_slice_number = 0
    
    def save_anonymized_file(self, filename, destination_folder):
        """ Method saves current image to destination_folder as filename. """
        pass
    
    def get_current_slice(self):
        """ Method returns array containing pixel data for current image. """
        pass

    def get_next_slice(self, value):
        """
        Method load next slice (for dicom or nifti images)
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
        ct_window, array = window.check_array_window_or_cut(self.pixel_array)
        return ct_window

    def get_info(self):
        array = self.pixel_array
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
        Methods makes lung segmentations.
        :return: numpy array with segmented area of lungs
        """
        raise NotImplementedError("Method should be overrided in derived classes.")


class DicomImage(ImageObject):
    """
    Class for representing dicom image object.
    """

    # List containing paths to all dicom images in source folder
    slices_path_list = []

    file_extensions = ["dcm", "DCM"]
    
    def __init__(self, folder, filename):
        
        super().__init__(folder, filename)
        self.file_type = ImageType.DCM
        self.image_object = anonym.get_anonymized_dicom(filename, folder)
        if self.image_object is None:
            raise TypeError("Error occurred during loading data.")
        self.pixel_array = self.image_object.pixel_array
        # Get filenames of all dicom files in source folder
        self.slices_path_list = [elem for elem in Path(self.src_folder).iterdir()
                                 if elem.is_file() and elem.suffix[1:] in self.file_extensions]
        self.total_slice_number = len(self.slices_path_list)
    
    def save_anonymized_file(self, filename, destination_folder):
        
        try:
            filename = self.get_filename_with_extension(filename)
            output_file_path = Path(destination_folder) / filename
            self.image_object.save_as(output_file_path)
            return True
        
        except Exception as ex:
            print(ex)
            return False
    
    def get_current_slice(self):
        
        return self.pixel_array
    
    def get_next_slice(self, value):
        
        if value >= self.total_slice_number:
            self.current_slice_number = self.total_slice_number - 1
        elif value <= 0:
            self.current_slice_number = 0
        else:
            self.current_slice_number = value
            
        self.src_filename = self.slices_path_list[value].name
        
        self.image_object = anonym.get_anonymized_dicom(self.src_filename, self.src_folder)
        self.pixel_array = self.image_object.pixel_array
        return self.pixel_array

    def check_ct_window(self):
        array = window.get_array_dicom_lut(self.src_filename, self.src_folder)
        ct_window, array = window.check_array_window_or_cut(array)
        return ct_window

    def get_segmented_lungs(self):
        gray_img = gray.get_grayscale_from_FileDataset(self.image_object)
        return sgKmeans.make_lungmask(gray_img, False)
        

class NiftiImage(ImageObject):
    """
    Class for representing nifti1 image object.
    """

    file_extensions = ["nii"]

    def __init__(self, folder, filename):
        
        super().__init__(folder, filename)
        self.file_type = ImageType.NIFTI
        self.image_object = anonym.get_anonymized_nifti(filename, folder)
        if self.image_object is None:
            raise TypeError("Error occurred during loading data.")
        self.pixel_array = self.image_object.get_fdata().T
        self.total_slice_number = self.image_object.shape[2]
    
    def save_anonymized_file(self, filename, destination_folder):
        
        try:
            filename = self.get_filename_with_extension(filename)
            output_file_path = Path(destination_folder) / filename
            nibabel.save(self.image_object, output_file_path)
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

    def get_segmented_lungs(self):
        raise TypeError("Nifti images not supported yet")


class JpgImage(ImageObject):
    """
    Class for representing jpg image object.
    """

    file_extensions = ["jpg", "jpeg", "JPG", "JPEG"]
    
    def __init__(self, folder, filename):
        
        super().__init__(folder, filename)
        self.file_type = ImageType.JPG
        self.image_object = anonym.get_anonymized_png_jpg(filename, folder)
        if self.image_object is None:
            raise TypeError("Error occurred during loading data.")
        self.pixel_array = np.array(self.image_object)
        self.total_slice_number = 1
    
    def save_anonymized_file(self, filename, destination_folder):
        
        try:
            filename = super().get_filename_with_extension(filename)
            output_file_path = Path(destination_folder) / filename
            self.image_object.save(output_file_path)
            return True
        
        except Exception as ex:
            print(ex)
            return False
    
    def get_current_slice(self):
        return self.pixel_array
    
    def get_next_slice(self, value):
        return self.pixel_array

    def get_segmented_lungs(self):
        gray_img = gray.get_grayscale_from_jpg_png(self.pixel_array)
        return sgKmeans.make_lungmask(gray_img, False)


class PngImage(ImageObject):
    """
    Class for representing png image object.
    """

    file_extensions = ["png", "PNG"]
    
    def __init__(self, folder, filename):
        
        super().__init__(folder, filename)
        self.file_type = ImageType.PNG
        self.image_object = anonym.get_anonymized_png_jpg(filename, folder)
        if self.image_object is None:
            raise TypeError("Error occurred during loading data.")
        self.pixel_array = np.array(self.image_object)
        self.total_slice_number = 1
    
    def save_anonymized_file(self, filename, destination_folder):
        
        try:
            filename = super().get_filename_with_extension(filename)
            output_file_path = Path(destination_folder) / filename
            self.image_object.save(output_file_path)
            return True
        
        except Exception as ex:
            print(ex)
            return False
    
    def get_current_slice(self):
        return self.pixel_array
    
    def get_next_slice(self, value):
        return self.pixel_array

    def get_segmented_lungs(self):
        gray_img = gray.get_grayscale_from_jpg_png(self.pixel_array)
        return sgKmeans.make_lungmask(gray_img, False)
