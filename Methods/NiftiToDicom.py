from pathlib import Path

import nibabel
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import SimpleITK as sitk


def convert_nifti1_to_dicom(src_file_path, dest_folder_location=""):
    """Function converts NIfTI file to DICOM collection"""

    # Odczytanie nazwy pliku bez rozszerzenia
    dest_folder_name = Path(src_file_path).stem
    slices_name = str(Path(src_file_path).stem)
    # Stworzenie folderu na zdjęcia
    destination_folder = Path(dest_folder_name)
    if not destination_folder.exists():
        destination_folder.mkdir()

    writer = sitk.ImageFileWriter()
    # Use the study/series/frame of reference information given in the meta-data
    # dictionary and not the automatically generated information from the file IO
    writer.KeepOriginalImageUIDOn()

    NiftyImg = sitk.ReadImage(str(src_file_path))
    Img_array = sitk.GetArrayViewFromImage(NiftyImg)
    new_img = sitk.GetImageFromArray(Img_array)
    new_img.SetSpacing([2.5, 3.5, 4.5])
    Slic_Num = len(Img_array)
    print(slices_name, Slic_Num)
    for slic in range(Slic_Num):
        DicomFileName = str(destination_folder / (slices_name + "-" + str(slic) + ".dcm"))
        writer.SetFileName(DicomFileName)
        writer.Execute(new_img[:, :, slic])
