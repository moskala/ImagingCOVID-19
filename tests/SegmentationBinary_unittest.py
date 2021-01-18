import unittest
import pydicom
import numpy as np
from pathlib import Path

from TestsContext import Methods
from Methods.LungSegmentation.MethodBinary import SegmentationB


class LungSegmentationMethodBDicomUnittest(unittest.TestCase):

    # testowy pacjent
    testDir = Path('test_data/testcase_dicom_hu/').resolve()
    testFile1 = 'testcase_hounsfield1.dcm'
    testFile2 = 'testcase_hounsfield2.dcm'

    def test_read_ct_scan(self):
        sgm = SegmentationB()
        scns = sgm.read_ct_scan(self.testDir)
        self.assertIsNotNone(scns)
        self.assertIsInstance(scns, np.ndarray)
        self.assertIsInstance(scns[0], np.ndarray)

    def test_get_segmented_lungs(self):
        test_file = self.testDir / self.testFile1
        arr = pydicom.read_file(test_file).pixel_array
        sgm = SegmentationB()
        im = sgm.get_segmented_lungs(arr)
        self.assertIsNotNone(im)
        self.assertIsInstance(im, np.ndarray)

    def test_segment_lung_from_ct_scan(self):
        test_file1 = self.testDir / self.testFile1
        test_file2 = self.testDir / self.testFile2
        lst = []
        file1 = pydicom.read_file(test_file1).pixel_array
        lst.append(file1)
        file2 = pydicom.read_file(test_file2).pixel_array
        lst.append(file2)
        sgm = SegmentationB()
        arr = sgm.segment_lung_from_ct_scan(lst, 1)
        self.assertIsNotNone(arr)
        self.assertEqual(len(arr), len(file2))
    
    def test_segment_lung_from_ct_scan_all(self):
        test_file1 = self.testDir / self.testFile1
        test_file2 = self.testDir / self.testFile2
        lst = []
        file1 = pydicom.read_file(test_file1).pixel_array
        lst.append(file1)
        file2 = pydicom.read_file(test_file2).pixel_array
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
