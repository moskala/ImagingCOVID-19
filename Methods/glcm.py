from skimage.feature import texture as ft
import numpy as np
import sys,os
from ImageClass import *
from matplotlib import pyplot as plt
from sklearn import svm
from pathlib import Path
sys.path.append(str(Path().resolve().parent / "Methods"))

from LungSegmentation.LungSegmentation_MethodB_dicom import SegmentationB
pi = np.pi
class Matrix:
    image_array = None
    def __init__(self, image_array):
        self.image_array = image_array.astype(np.uint8)

    def GetMatrix(self,distances=[5],angles=[0,pi/4,pi/2,3*pi/4]):
        return ft.greycomatrix(self.image_array,distances,angles)
    
    def GetMatrixPatch(self,patch,distances,angles):
        return ft.greycomatrix(patch,distances,angles)

    def GetProps(self):
        mtrx = self.GetMatrix()
        return [ft.greycoprops(mtrx,prop='contrast'),
                ft.greycoprops(mtrx,prop='correlation'),
                ft.greycoprops(mtrx,prop='energy'),
                ft.greycoprops(mtrx,prop='homogeneity')]

class Model:
    model = None
    def __init__(self):
        self.model = svm.SVC()
    
    def FitModel(self,data,labels):
        self.model.fit(data,labels)
    
    def PredictModel(self,data):
        return self.model.predict(data)

class ImageEnsemble:
    folders = None
    dicoms = None
    lungs = None
    matrices = None
    props = None
    def __init__(self,folders):
        self.folders = folders
    
    def MakeDicoms(self):
        self.dicoms=[]
        for folder in self.folders:
            patient=[]
            for fl in os.listdir(folder):
                patient.append(DicomImage(folder,fl))
            self.dicoms.append(patient)

    def GetLungs(self):
        self.lungs = []
        for dcm in self.dicoms:
            patient=[]
            for slc in dcm:
                patient.append(SegmentationB.get_segmented_lungs(slc.get_current_slice()))
            self.lungs.append(patient)
        

    def GetMatrices(self):
        self.matrices=[]
        for patient in self.lungs:
            arrays=[]
            for array in patient:
                arrays.append(Matrix(array))
            self.matrices.append(arrays)
    
    def GetProps(self):
        self.props=[]
        for arrays in self.matrices:
            pp=[]
            for array in arrays:
                pp.append(array.GetProps())
            self.props.append(pp)

    



e = ImageEnsemble([r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\wloch1"])
e.MakeDicoms()
e.GetLungs()
e.GetMatrices()
e.GetProps()
print(e.props[0][65])

# plt.imshow(l[0][65],cmap='gray')
# plt.show()



    
