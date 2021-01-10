import unittest
import sys
from pathlib import Path
sys.path.append(str(Path().resolve().parent))
from Alexnet import *
from alexnet_pytorch import AlexNet
sys.path.append(str(Path().resolve().parent))
from ImageMedical.ImageClass import *

class TestAlex(unittest.TestCase):
    test_folder = r"C:\Users\Maya\studia\4rok\inz\repo\ImagingCOVID-19\Methods\tests\test_data\test_classification"
    test_file = r"testDicom.dcm"
    model_path = str(Path().resolve().parent.parent.parent / "models" / "featureExtraction.joblib")

    def test_basic(self):
        model = Alex(model=load(self.model_path))
        self.assertIsInstance(model.alex,AlexNet)
        fts = model.GetFeatures(DicomImage(self.test_folder,self.test_file).get_current_slice())
        self.assertEqual(fts.size(),torch.Size([1, 256, 6, 6]))

    def test_change_dim(self):
        model = Alex(model=load(self.model_path))
        fts = model.GetFeatures(DicomImage(self.test_folder,self.test_file).get_current_slice())
        chng = model.ChangeDimAndStandardize([fts])
        self.assertEqual(len(chng[0]),256)

    def test_pca(self):
        model = Alex(model=load(self.model_path))
        fts = model.GetFeatures(DicomImage(self.test_folder,self.test_file).get_current_slice())
        chng = model.ChangeDimAndStandardize([fts,fts])
        pc = model.DoPCA(chng,n=2)
        self.assertIsNotNone(pc)


if __name__ == '__main__':
    unittest.main()