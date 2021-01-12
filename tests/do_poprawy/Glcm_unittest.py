import unittest
from sklearn import svm
from pathlib import Path

from TestsContext import Methods
from Methods.Glcm import ImageEnsemble, Matrix, Model


class TestGLCM(unittest.TestCase):

    test_folder = Path('../test_data/testcase_dicom_hu').resolve()
    test_file = 'testcase_hounsfield1.dcm'

    def test_image_ensebmle(self):
        e = ImageEnsemble([str(self.test_folder)], gotFolders=True)
        e.MakeDicoms()
        # e.GetLungs()
        e.GetMatrices()
        e.GetProps()
        self.assertIsNotNone(e.props)
        self.assertEqual(len(e.dicoms), 1)
        self.assertEqual(len(e.matrices), 1)
        self.assertEqual(len(e.matrices[0].image_array), len(e.lungs[0]))
        self.assertEqual(len(e.props[0]), 16)
        self.assertIsInstance(e.matrices[0], Matrix)

    def test_matrix(self):
        e = ImageEnsemble()
        e.MakeDicoms(self.test_folder, self.test_file)
        mtrx = e.dicoms[0]
        array = Matrix(mtrx.get_current_slice())
        glc = array.GetMatrix()
        props = array.GetPropsFromMatrix()
        self.assertIsNotNone(props)
        self.assertEqual(len(mtrx.get_current_slice()), 512)
        self.assertEqual(len(glc), 256)

    def test_model(self):
        svmModel = Model()
        self.assertIsInstance(svmModel.model, svm.SVC)


if __name__ == '__main__':
    unittest.main()
