# Dokument opisujący standardy anonimizacji zdjęć dicom:
# http://dicom.nema.org/dicom/2013/output/chtml/part15/chapter_E.html#table_E.1-1

# Przydante informacje o formacie dicom:
# https://nipy.org/nibabel/dicom/dicom_intro.html#dicom-data-format

import dicomanonymizer
import pydicom
from pathlib import Path


# Metoda 1 - biblioteka dicomanonymizer

def anonymize_dicom(input_file_path, output_file_path):
    dicomanonymizer.anonymizeDICOMFile(input_file_path, output_file_path)

# Metoda 2 - biblioteka pydicom

def anonymize_selected_tags(input_file_path, output_file_path):
    dataset = pydicom.dcmread(input_file_path)
    data_elements = dataset.dir("patient")  # Wszystkie tagi zawierające w nazwie "patient"
    for data_element in data_elements:
        del dataset[data_element]
        
    dataset.save_as(output_file_path)
    

# Przykład

def sample_exec():
    input_path = Path('sample_data') / 'MR_small.dcm'
    output_path = Path('sample_data') / 'MR_small_anonymized.dcm'

    anonymize_dicom(input_path, output_path)

    # Można zobaczyć listę etykiet przed i po
    # print(list(pydicom.dcmread(input_path)))
    # print(list(pydicom.dcmread(output_path)))







