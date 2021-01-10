import unittest
import sys
from sklearn import svm
from pathlib import Path
sys.path.append(str(Path().resolve().parent))
from Glcm import *

class TestGLCM(unittest.TestCase):
    test_folder = r"C:\Users\Maya\studia\4rok\inz\repo\ImagingCOVID-19\Methods\tests\test_data\test_classification"
    test_file = r"testDicom.dcm"
    def test_image_ensebmle(self):
        e = ImageEnsemble([self.test_folder],gotFolders=True)
        e.MakeDicoms()
        e.GetLungs()
        e.GetMatrices()
        e.GetProps()
        self.assertIsNotNone(e.props)
        self.assertEqual(len(e.dicoms),1)
        self.assertEqual(len(e.matrices),1)
        self.assertEqual(len(e.matrices[0].image_array),len(e.lungs[0]))
        self.assertEqual(len(e.props[0]),16)
        self.assertIsInstance(e.matrices[0],Matrix)

    def test_matrix(self):
        e = ImageEnsemble()
        e.MakeDicoms(self.test_folder,self.test_file)
        mtrx = e.dicoms[0]
        array = Matrix(mtrx.get_current_slice())
        glc = array.GetMatrix()
        props = array.GetPropsFromMatrix()
        self.assertIsNotNone(props)
        self.assertEqual(len(mtrx.get_current_slice()),512)
        self.assertEqual(len(glc),256)

    def test_model(self):
        svmModel = Model()
        self.assertIsInstance(svmModel.model,svm.SVC)

if __name__ == '__main__':
    unittest.main()
