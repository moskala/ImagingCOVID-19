import unittest
import sys
from pathlib import Path
import numpy as np
import pydicom
import nibabel
import PIL
import ParamsLists as param

from TestsContext import Methods

import Methods.Grayscale as gray


class TestGrayscaleMethods(unittest.TestCase):

    test_data_folder = Path('test_data').resolve()

    def test_array_values_in_interval(self):
        test_array = np.random.randint(low=-300, high=500, size=(100, 100))
        gray_array = gray.convert_array_to_grayscale(test_array)
        min_val = np.min(gray_array)
        max_val = np.max(gray_array)
        self.assertTrue(min_val >= 0)
        self.assertTrue(max_val <= 255)

    def test_convert_rgb_to_grayscale(self):
        test_array = np.random.randint(low=0, high=256, size=9000).reshape([50, 60, 3])
        gray_array = gray.convert_rgb_to_grayscale(test_array)
        min_val = np.min(gray_array)
        max_val = np.max(gray_array)
        self.assertTrue(gray_array.ndim == 2)
        self.assertTrue(min_val >= 0)
        self.assertTrue(max_val <= 255)

    def test_get_grayscale_from_dicom(self):
        dcm_folder = str(self.test_data_folder / 'testcase_dicom_hu')
        for file_name in param.param_list_dcm_hu:
            with self.subTest("Test for file: {0}".format(file_name)):
                gray_array = \
                    gray.get_grayscale_from_dicom(file_name, dcm_folder)
                self.assertIsNotNone(gray_array)
                min_val = np.min(gray_array)
                max_val = np.max(gray_array)
                self.assertTrue(gray_array.ndim == 2)
                self.assertTrue(min_val >= 0)
                self.assertTrue(max_val <= 255)

    def test_get_grayscale_from_nii(self):
        nii_folder = str(self.test_data_folder / 'testcase_nifti')

        for file_name in param.param_list_nii[0:1]:
            with self.subTest("Test for file: {0}".format(file_name)):
                gray_array = \
                    gray.get_grayscale_from_nifti(file_name, nii_folder)
                self.assertIsNotNone(gray_array)
                min_val = np.min(gray_array)
                max_val = np.max(gray_array)
                self.assertTrue(gray_array.ndim >= 2)
                self.assertTrue(min_val >= 0)
                self.assertTrue(max_val <= 255)

    def test_get_grayscale_from_jpg(self):
        folder = str(self.test_data_folder / "testcase_jpg_png")

        for file_name in param.param_list_jpg:
            with self.subTest("Test for file: {0}".format(file_name)):
                gray_array = \
                    gray.get_grayscale_from_jpg_png(file_name, folder)
                self.assertIsNotNone(gray_array)
                min_val = np.min(gray_array)
                max_val = np.max(gray_array)
                self.assertTrue(gray_array.ndim == 2)
                self.assertTrue(min_val >= 0)
                self.assertTrue(max_val <= 255)

    def test_get_grayscale_from_pnd(self):
        folder = str(self.test_data_folder / "testcase_jpg_png")

        for file_name in param.param_list_png:
            with self.subTest("Test for file: {0}".format(file_name)):
                gray_array = \
                    gray.get_grayscale_from_jpg_png(file_name, folder)
                self.assertIsNotNone(gray_array)
                min_val = np.min(gray_array)
                max_val = np.max(gray_array)
                self.assertTrue(gray_array.ndim == 2)
                self.assertTrue(min_val >= 0)
                self.assertTrue(max_val <= 255)


if __name__ == '__main__':
    unittest.main()
