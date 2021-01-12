import unittest
import sys
from pathlib import Path
import pydicom
import nibabel
import PIL
import ParamsLists as param

from TestsContext import Methods
import Methods.Anonymize.Anonymization as anonym


class TestAnonymizationMethods(unittest.TestCase):

    test_data_folder = Path("test_data").resolve()

    def test_png_if_not_none(self):
        folder = self.test_data_folder / "testcase_jpg_png"
        for file_name in param.param_list_png:
            with self.subTest("Test for file: {0}".format(file_name)):
                result = \
                    anonym.get_anonymized_png_jpg(file_name, str(folder))
                self.assertIsNotNone(result)

    def test_jpg_if_not_none(self):
        folder = self.test_data_folder / "testcase_jpg_png"
        for file_name in param.param_list_jpg:
            with self.subTest("Test for file: {0}".format(file_name)):
                result = \
                    anonym.get_anonymized_png_jpg(file_name, str(folder))
                self.assertIsNotNone(result)

    def test_nifit_if_not_none(self):
        folder = self.test_data_folder / "testcase_nifti"
        for file_name in param.param_list_nii:
            with self.subTest("Test for file: {0}".format(file_name)):
                result = \
                    anonym.get_anonymized_nifti(file_name, str(folder))
                self.assertIsNotNone(result)

    def test_dicom_if_not_none(self):
        dcm_folder = str(self.test_data_folder / "testcase_dicom_gray")
        for file_name in param.param_list_dcm_gray:
            with self.subTest("Test for file: {0}".format(file_name)):
                result = \
                    anonym.get_anonymized_dicom(file_name, dcm_folder)
                self.assertIsNotNone(result)

    def test_png_is_none(self):
        folder = self.test_data_folder / "testcase_jpg_png"
        file_name = "this_file_not_exists.png"
        result = \
            anonym.get_anonymized_png_jpg(file_name, str(folder))
        self.assertIsNone(result)

    def test_jpg_is_none(self):
        folder = self.test_data_folder / "testcase_jpg_png"
        file_name = "this_file_not_exists.jpg"
        result = \
            anonym.get_anonymized_png_jpg(file_name, str(folder))
        self.assertIsNone(result)

    def test_nifti_is_none(self):
        folder = self.test_data_folder / "testcase_nifti"
        file_name = "this_file_not_exists.nii"
        result = \
            anonym.get_anonymized_nifti(file_name, str(folder))
        self.assertIsNone(result)

    def test_dcm_is_none(self):
        dcm_folder = str(self.test_data_folder / "testcase_dicom_gray")
        file_name = "this_file_not_exists.dcm"
        result = \
            anonym.get_anonymized_dicom(file_name, str(dcm_folder))
        self.assertIsNone(result)

    def test_dcm_type(self):
        dcm_folder = str(self.test_data_folder / "testcase_dicom_gray")
        for file_name in param.param_list_dcm_gray:
            with self.subTest("Test for file: {0}".format(file_name)):
                result = \
                    anonym.get_anonymized_dicom(file_name, dcm_folder)
                self.assertIsInstance(type(result), type(pydicom.FileDataset))

    def test_nifit_type(self):
        folder = self.test_data_folder / "testcase_nifti"
        for file_name in param.param_list_nii:
            with self.subTest("Test for file: {0}".format(file_name)):
                result = \
                    anonym.get_anonymized_nifti(file_name, str(folder))
                self.assertIsInstance(type(result), type(nibabel.nifti1.Nifti1Image))

    def test_png_type(self):
        folder = self.test_data_folder / "testcase_jpg_png"
        for file_name in param.param_list_png:
            with self.subTest("Test for file: {0}".format(file_name)):
                result = \
                    anonym.get_anonymized_png_jpg(file_name, str(folder))
                self.assertIsInstance(type(result), type(PIL.Image.Image))

    def test_jpg_type(self):
        folder = self.test_data_folder / "testcase_jpg_png"
        for file_name in param.param_list_jpg:
            with self.subTest("Test for file: {0}".format(file_name)):
                result = \
                    anonym.get_anonymized_png_jpg(file_name, str(folder))
                self.assertIsInstance(type(result), type(PIL.Image.Image))


if __name__ == '__main__':
    unittest.main()
