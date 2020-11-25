
import unittest
import sys, os
import pydicom
import numpy as np
from pathlib import Path

#sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Methods'))
sys.path.append(str(Path().resolve().parent))

from LungSegmentation.LungSegmentation_MethodA_dicom import SegmentationA

# testowy pacjent
testDir = 'test_data/79262/'
testFile = 'test_data/79262/1-001.dcm'

# print(version('unittest'))


class LungSegmentationMethodADicomUnittest(unittest.TestCase):
    def test_load_scan(self):
        slices = SegmentationA.load_scan(Path(testDir))
        self.assertEqual(len(slices), len(os.listdir(Path(testDir))),
                         "Number of slices should equal the number of dcm files in test folder")
        self.assertIsNotNone(slices)
        self.assertIsInstance(slices, list)

    def test_get_pixels_hu(self):
        lst = [pydicom.read_file(testFile)]
        arr = SegmentationA.get_pixels_hu(lst)
        self.assertIsInstance(arr,np.ndarray)
        self.assertFalse(arr.any() == -2000)
    
    def test_seperate_lungs(self):
        pxls = np.stack(pydicom.read_file(testFile).pixel_array)
        # powinno zwrocic tuple np.ndarray
        lungs = SegmentationA.seperate_lungs(pxls)
        self.assertIsNotNone(lungs)
        self.assertIsInstance(lungs[0], np.ndarray)


if __name__ == '__main__':
    unittest.main()
