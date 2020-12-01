from pathlib import Path
import nibabel
from PIL import Image
import dicomanonymizer
import pydicom


def get_anonymized_nifti(file_name: str, input_folder: str):
    """
    Function performs anonymization of given file of nifti1 type.
    Function load file from given folder and empty set 'extra' from image frame.
    It returns object of nibabel.nifti1.Nifti1Image type. 
    If file does not exists or other error occurs, None object is returned instead. 

    :param file_name: file name of source image
    :param input_folder: name of folder containing given file
    :return: output_folder: anonymized Nifti1Image or None object
    """

    input_file_path = Path(input_folder) / file_name
    try:
        img = nibabel.load(input_file_path)

        if img.extra:
            img.extra = {}

        return img
    
    except FileNotFoundError:
        print("File {0} not found".format(input_file_path))
    except Exception as ex:
        print(ex)

    return None


def get_anonymized_png_jpg(file_name: str, input_folder: str):
    """"
    Function performs anonymization of given file of jpg or png type.
    Function load file from given folder and creates new image without exif data.
    It returns object of PIL.Image.Image type. 
    If file does not exists or other error occurs, None object is returned instead. 

    :param file_name: file name of source image
    :param input_folder: name of folder containing given file
    :return: output_folder: anonymized Image or None object
    """
    input_file_path = Path(input_folder) / file_name
    try:
        image = Image.open(input_file_path)

        data = list(image.getdata())

        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)

        return image_without_exif

    except FileNotFoundError:
        print("File {0} not found".format(input_file_path))
    except Exception as ex:
        print(ex)

    return None


def get_anonymized_dicom(file_name: str, input_folder: str):
    """
    Function performs anonymization of given file of dicom type.
    Function uses method anonymizeDataset from dicomanonymizer package,
    which anonymize file according to the standards. 
    It returns object of pydicom.dataset.FileDataset type. 
    If file does not exists or other error occurs, None object is returned instead. 

    :param file_name: file name of source image
    :param input_folder: name of folder containing given file
    :return: output_folder: anonymized FileDataset or None object
    """
    try:
        input_file_path = Path(input_folder) / file_name
        ds = pydicom.dcmread(input_file_path)
        dicomanonymizer.anonymizeDataset(ds)
        return ds

    except FileNotFoundError:
        print("File {0} not found".format(input_file_path))
    except Exception as ex:
        print(ex)

    return None


