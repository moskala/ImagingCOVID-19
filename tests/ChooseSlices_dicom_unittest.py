import unittest
import os,sys
import dicom
import numpy as np
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'Methods'))
from ChooseSlices import ChooseSlices

testDir = Path('/Users/Maya/studia/4rok/inz/repo/ImagingCOVID-19/tests/test_data/79262/')

class ChooseSlices_dicom_unittest(unittest.TestCase):
    def test_choose(self):
        cs = ChooseSlices()
        ind = cs.choose(testDir,0.1)
        self.assertIsNotNone(ind)
        self.assertTrue(len(ind)>0)

if __name__ == '__main__':
    unittest.main()