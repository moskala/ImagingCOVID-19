from pathlib import Path
import nibabel
from PIL import Image
import dicomanonymizer

def anonymize_nii(file_name: str, input_folder: str, output_folder: str):
    """
    Funkcja przeprowadza anonimizację na obrazu formatu nii.
    Zbiór 'extra' jest zastępowany pustym zbiorem.
    Funkcja zapisuje zanonimizowany obraz jest we wskazanym folderze.
    Zwraca ścieżkę do nowego obrazu lub None.

    :param file_name: nazwa pliku do zanonimizowania
    :param input_folder: nazwa folderu zwierającego plik
    :param output_folder: nazwa folderu docelowego
    :return: ścieżka do nowego obrazu lub None
    """

    input_file_path = Path(input_folder) / file_name
    try:
        img = nibabel.load(input_file_path)

        if img.extra:
            img.extra = {}

        output_file_path = Path(output_folder) / ("anonymized_" + file_name)

        nibabel.save(img, output_file_path)

        return output_file_path
    except FileNotFoundError:
        print("File {0} not found".format(input_file_path))
    except Exception as ex:
        print(ex.message)

    return None


def anonymize_png_jpg(file_name: str, input_folder: str, output_folder: str):
    """"
    Funkcja przeprowadza anonimizację na zdjęciach formatu png i jpg.
    Usuwany jest zbiór danych exif.
    Funkcja zapisuje zanonimizowane zdjęcie w docelowym folderze.
    Zwraca ścieżkę do nowego obrazu lub None.

    :param file_name: nazwa pliku do zanonimizowania
    :param input_folder: nazwa folderu zwierającego plik
    :param output_folder: nazwa folderu docelowego
    :return: ścieżka do nowego obrazu lub None
    """
    input_file_path = Path(input_folder) / file_name
    try:
        image = Image.open(input_file_path)

        data = list(image.getdata())

        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)

        output_file_path = Path(output_folder) / ("exif_stripped_" + file_name)
        image_without_exif.save(output_file_path)

        return output_file_path

        print("File saved: {0}".format(output_file_path))
    except FileNotFoundError:
        print("File {0} not found".format(input_file_path))
    except Exception as ex:
        print(ex.message)

    return None


def anonymize_dicom(file_name: str, input_folder: str, output_folder: str):
    """
    Funkcja przeprowadza anonimizację na zdjęciach formatu dicom.
    Korzysta z metody anonymizeDICOMFile z biblioteki dicomanonymizer,
    która anonimizuje plik zgodnie ze standardem.
    Funkcja zapisuje zanonimizowane zdjęcie w docelowym folderze.
    Zwraca ścieżkę do nowego obrazu lub None.

    :param file_name: nazwa pliku do zanonimizowania
    :param input_folder: nazwa folderu zwierającego plik
    :param output_folder: nazwa folderu docelowego
    :return: ścieżka do nowego obrazu lub None
    """

    input_file_path = Path(input_folder) / file_name
    output_file_path = Path(output_folder) / ("anonymized_" + file_name)

    try:
        dicomanonymizer.anonymizeDICOMFile(input_file_path, output_file_path)
        return output_file_path
    except FileNotFoundError:
        print("File {0} not found".format(input_file_path))
    except Exception as ex:
        print(ex)

    return None



