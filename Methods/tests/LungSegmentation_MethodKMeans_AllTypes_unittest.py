import unittest
import sys
from pathlib import Path
import pydicom
import nibabel
import PIL
import ParamsLists as param

sys.path.append(str(Path().resolve().parent / "LungSegmentation"))
from LungSegmentation_MethodKMeans_AllTypes import *


class TestAnonymizationMethods(unittest.TestCase):
    test_data_folder = Path(r"D:\Studia\sem7\inzynierka\aplikacja\test_data")

    def test_raise_error(self):
        img = np.zeros(900).reshape([30, 30])
        with self.assertRaises(Exception):
            make_lungmask(img, False)

    def test_not_null(self):
        image = gray.get_grayscale_from_dicom("Italy_case010060.dcm",
                                              str(Path().resolve().parent.parent.parent / "images_data" / "pacjent_dcm" ))
        mask = make_lungmask(image, False)
        self.assertIsNotNone(mask)


if __name__ == '__main__':
    unittest.main()