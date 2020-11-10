import unittest
import sys
from pathlib import (Path)

import ParamsLists as param

sys.path.append(str(Path().resolve().parent / "Anonymize"))

import Anonymization_Functions as anonym


class TestAnonymizationMethods(unittest.TestCase):

    test_data_folder = Path("test_data")
    test_output_folder = Path("test_data/test_anonymized_output")

    def test_png_if_exists(self):
        for file_name in param.param_list_png:
            with self.subTest("Test for file: {0}".format(file_name)):
                output_file_path = \
                    anonym.anonymize_png_jpg(file_name, str(self.test_data_folder), str(self.test_output_folder))
                self.assertIsNotNone(output_file_path)
                output_file = Path(output_file_path)
                self.assertIs(output_file.is_file(), True)

    def test_jpg_if_exists(self):

        for file_name in param.param_list_jpg:
            with self.subTest("Test for file: {0}".format(file_name)):
                output_file_path = \
                    anonym.anonymize_png_jpg(file_name, str(self.test_data_folder), str(self.test_output_folder))
                self.assertIsNotNone(output_file_path)
                output_file = Path(output_file_path)
                self.assertIs(output_file.is_file(), True)

    def test_nii_if_exists(self):

        for file_name in param.param_list_nii:
            with self.subTest("Test for file: {0}".format(file_name)):
                output_file_path = \
                    anonym.anonymize_nii(file_name, str(self.test_data_folder), str(self.test_output_folder))
                self.assertIsNotNone(output_file_path)
                output_file = Path(output_file_path)
                self.assertIs(output_file.is_file(), True)

    def test_dicom_if_exists(self):
        for file_name in param.param_list_dcm:
            with self.subTest("Test for file: {0}".format(file_name)):
                output_file_path = \
                    anonym.anonymize_dicom(file_name, str(self.test_data_folder), str(self.test_output_folder))
                self.assertIsNotNone(output_file_path)
                output_file = Path(output_file_path)
                self.assertIs(output_file.is_file(), True)

    def test_png_is_none(self):
        file_name = "this_file_not_exists"
        output_file_path = \
            anonym.anonymize_png_jpg(file_name, str(self.test_data_folder), str(self.test_output_folder))
        self.assertIsNone(output_file_path)

    def test_jpg_is_none(self):
        file_name = "this_file_not_exists"
        output_file_path = \
            anonym.anonymize_png_jpg(file_name, str(self.test_data_folder), str(self.test_output_folder))
        self.assertIsNone(output_file_path)

    def test_nii_is_none(self):
        file_name = "this_file_not_exists"
        output_file_path = \
            anonym.anonymize_nii(file_name, str(self.test_data_folder), str(self.test_output_folder))
        self.assertIsNone(output_file_path)

    def test_dcm_is_none(self):
        file_name = "this_file_not_exists"
        output_file_path = \
            anonym.anonymize_dicom(file_name, str(self.test_data_folder), str(self.test_output_folder))
        self.assertIsNone(output_file_path)


def prepare_output_directory(folder_name):
    folder = Path(folder_name)
    if folder.exists():
        for file in folder.iterdir():
            if file.is_file():
                file.unlink()
    else:
        folder.mkdir(parents=True)


if __name__ == '__main__':
    prepare_output_directory(TestAnonymizationMethods.test_output_folder)
    unittest.main()
