from skimage.feature import texture as ft
import numpy as np
import sys,os,time
from ImageClass import *
from matplotlib import pyplot as plt
from sklearn import svm
from pathlib import Path
from sklearn.model_selection import cross_val_score
sys.path.append(str(Path().resolve().parent / "Methods"))


from LungSegmentation.LungSegmentation_MethodKMeans_AllTypes import *
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

    def CrossValidate(self,data,labels,cv=5):
        return cross_val_score(self.model,data,labels,cv=cv)

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
                patient.append(make_lungmask(slc.get_current_slice()))
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

    


stime = time.time()
e = ImageEnsemble(os.path.join(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs"))
e.MakeDicoms()
e.GetLungs()
e.GetMatrices()
e.GetProps()
print(e.props)
print('Making matrices - execution time: ',time.time()-stime)
# print(len(e.props)," ",len(e.props[0])," ",len(e.props[0][0]))

labels = ['covid','covid','covid','covid','covid','normal','normal','normal','normal','normal']
model = Model()
print(model.CrossValidate(e.props,labels))
print('Making matrices + 5-fold x validation - execution time: ',time.time()-stime)

# plt.imshow(l[0][65],cmap='gray')
# plt.show()



    
