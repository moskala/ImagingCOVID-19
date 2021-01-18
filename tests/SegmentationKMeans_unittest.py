import unittest
from pathlib import Path
import numpy as np

from TestsContext import Methods
import Methods.LungSegmentation.MethodKMeans as sgm
import Methods.Grayscale as gray


class TestKMeansSegmentationMethods(unittest.TestCase):

    test_data_folder_hu = Path('test_data/testcase_dicom_hu').resolve()
    test_file = 'testcase_hounsfield1.dcm'

    def test_raise_error(self):
        img = np.zeros(900).reshape([30, 30])
        with self.assertRaises(Exception):
            sgm.make_lungmask(img, False)

    def test_not_null(self):
        image = gray.get_grayscale_from_dicom(self.test_file, self.test_data_folder_hu)
        mask = sgm.make_lungmask(image, False)
        self.assertIsNotNone(mask)


if __name__ == '__main__':
    unittest.main()