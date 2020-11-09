from pathlib import Path
import nibabel
from PIL import Image
import dicomanonymizer


def anonymize_nii(folder_name: str, file_name: str):
    """
    Funkcja przeprowadza anonimizację na zdjęciach formatu nii.
    Zbiór 'extra' jest zastępowany pustym zbiorem.
    Funkcja zapisuje zanonimizowane zdjęcie w tym samym folderze.
    Zwraca ścieżkę do nowego zdjęcia.

    :param folder_name: nazwa folderu zwierającego plik
    :param file_name: nazwa pliku do zanonimizowania
    :return: ścieżka do nowego zdjęcia
    """

    folder = Path(folder_name)
    input_file_path = folder / file_name
    try:
        img = nibabel.load(input_file_path)
    except FileNotFoundError:
        print("File {0} not found".format(input_file_path))
    except Exception as ex:
        print(ex.message)

    if img.extra:
        img.extra = {}

    output_file_path = folder / ("anonymized_" + file_name)

    nibabel.save(img, output_file_path)

    return output_file_path


def anonymize_png_jpg(folder_name: str, file_name: str):
    """"
    Funkcja przeprowadza anonimizację na zdjęciach formatu png i jpg.
    Usuwany jest zbiór danych exif.
    Funkcja zapisuje zanonimizowane zdjęcie w tym samym folderze.
    Zwraca ścieżkę do nowego zdjęcia.

    :param folder_name: nazwa folderu zwierającego plik
    :param file_name: nazwa pliku do zanonimizowania
    :return: ścieżka do nowego zdjęcia
    """
    input_file_path = Path(folder_name) / file_name
    try:
        image = Image.open(input_file_path)
    except FileNotFoundError:
        print("File {0} not found".format(input_file_path))
    except Exception as ex:
        print(ex.message)

    data = list(image.getdata())

    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    output_file_path = Path(folder_name) / ("exif_stripped_" + file_name)
    image_without_exif.save(output_file_path)

    print("File saved: {0}".format(output_file_path))

    return output_file_path


def anonymize_dicom(folder_name: str, file_name: str):
    """
    Funkcja przeprowadza anonimizację na zdjęciach formatu dicom.
    Korzysta z metody anonymizeDICOMFile z biblioteki dicomanonymizer,
    która anonimizuje plik zgodnie ze standardem.
    Funkcja zapisuje zanonimizowane zdjęcie w tym samym folderze.

    :param folder_name: nazwa folderu zwierającego plik
    :param file_name: nazwa pliku do zanonimizowania
    :return: ścieżka do nowego zdjęcia
    """

    folder = Path(folder_name)
    input_file_path = folder / file_name
    output_file_path = folder / ("anonymized_" + file_name)

    try:
        dicomanonymizer.anonymizeDICOMFile(input_file_path, output_file_path)
    except FileNotFoundError:
        print("File {0} not found".format(input_file_path))
    except Exception as ex:
        print(ex.message)

    return output_file_path

