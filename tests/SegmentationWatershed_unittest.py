import unittest
import os
import pydicom
import numpy as np
from pathlib import Path

from TestsContext import Methods
from Methods.LungSegmentation.MethodWatershed import SegmentationA


class LungSegmentationMethodWatershedDicomUnittest(unittest.TestCase):

    # testowy pacjent
    testDir = 'test_data/testcase_dicom_hu'
    testFile = 'testcase_hounsfield1.dcm'

    def test_load_scan(self):
        full_path = Path(self.testDir).resolve()
        slices = SegmentationA.load_scan(full_path)
        self.assertEqual(len(slices), len(os.listdir(full_path)),
                         "Number of slices should equal the number of dcm files in test folder")
        self.assertIsNotNone(slices)
        self.assertIsInstance(slices, list)

    def test_get_pixels_hu(self):
        full_path = Path(self.testDir).resolve() / self.testFile
        lst = [pydicom.read_file(full_path)]
        arr = SegmentationA.get_pixels_hu(lst)
        self.assertIsInstance(arr, np.ndarray)
        self.assertFalse(arr.any() == -2000)
    
    def test_seperate_lungs(self):
        full_path = Path(self.testDir).resolve() / self.testFile
        pxls = np.stack(pydicom.read_file(full_path).pixel_array)
        # should return tuple np.ndarray
        lungs = SegmentationA.seperate_lungs(pxls)
        self.assertIsNotNone(lungs)
        self.assertIsInstance(lungs[0], np.ndarray)


if __name__ == '__main__':
    unittest.main()
