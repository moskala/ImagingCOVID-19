import unittest
import os, sys
import pydicom
import numpy as np
from pathlib import Path

#sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Methods'))
sys.path.append(str(Path().resolve().parent))

from LungSegmentation.LungSegmentation_MethodB_dicom import SegmentationB

# testowy pacjent
testDir = 'test_data/79262/'
testFile = 'test_data/79262/1-001.dcm'
testFile2 = 'test_data/79262/1-050.dcm'


class LungSegmentationMethodBDicomUnittest(unittest.TestCase):
    def test_read_ct_scan(self):
        sgm = SegmentationB()
        scns = sgm.read_ct_scan(testDir)
        self.assertIsNotNone(scns)
        self.assertIsInstance(scns, np.ndarray)
        self.assertIsInstance(scns[0], np.ndarray)

    def test_get_segmented_lungs(self):
        arr = pydicom.read_file(testFile).pixel_array
        sgm = SegmentationB()
        im = sgm.get_segmented_lungs(arr)
        self.assertIsNotNone(im)
        self.assertIsInstance(im, np.ndarray)

    def test_segment_lung_from_ct_scan(self):
        lst = []
        file1 = pydicom.read_file(testFile).pixel_array
        lst.append(file1)
        file2 = pydicom.read_file(testFile2).pixel_array
        lst.append(file2)
        sgm = SegmentationB()
        arr=sgm.segment_lung_from_ct_scan(lst,1)
        self.assertIsNotNone(arr)
        self.assertEqual(len(arr),len(file2))
    
    def test_segment_lung_from_ct_scan_all(self):
        lst = []
        file1 = pydicom.read_file(testFile).pixel_array
        lst.append(file1)
        file2 = pydicom.read_file(testFile2).pixel_array
        lst.append(file2)
        sgm = SegmentationB()
        arr = sgm.segment_lung_from_ct_scan_all(lst)
        hm = 0
        for a in arr:
            hm = hm + len(a)
        self.assertIsNotNone(arr)
        self.assertEqual(hm, len(file2) + len(file1))


if __name__ == '__main__':
    unittest.main()
