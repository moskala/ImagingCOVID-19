import unittest
from pathlib import Path
from alexnet_pytorch import AlexNet
import os
import torch

from TestsContext import Methods
from Methods.Alexnet import Alex, load
from Methods.ImageMedical.ImageClass import DicomImage


class TestAlex(unittest.TestCase):

    test_folder = Path('test_data/testcase_dicom_hu').resolve()
    test_file = 'testcase_hounsfield1.dcm'
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                              'models', 'ct', 'featureExtraction.joblib'))

    def test_basic(self):
        model = Alex(model=load(self.model_path))
        self.assertIsInstance(model.alex, AlexNet)
        fts = model.GetFeatures(DicomImage(self.test_folder, self.test_file).get_current_slice())
        self.assertEqual(fts.size(), torch.Size([1, 256, 6, 6]))

    def test_change_dim(self):
        model = Alex(model=load(self.model_path))
        fts = model.GetFeatures(DicomImage(self.test_folder, self.test_file).get_current_slice())
        chng = model.ChangeDimAndStandardize([fts])
        self.assertEqual(len(chng[0]), 256)

    def test_pca(self):
        model = Alex(model=load(self.model_path))
        fts = model.GetFeatures(DicomImage(self.test_folder, self.test_file).get_current_slice())
        chng = model.ChangeDimAndStandardize([fts, fts])
        pc = model.DoPCA(chng, n=2)
        self.assertIsNotNone(pc)


if __name__ == '__main__':
    unittest.main()
