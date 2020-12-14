from joblib import dump, load
from skimage.feature import texture as ft
import numpy as np
import sys,os,time
from ImageClass import *
from matplotlib import pyplot as plt
from sklearn import svm
from pathlib import Path
from sklearn.model_selection import cross_val_score
sys.path.append(str(Path().resolve().parent / "Methods"))

'''this script contains classes necessary to implement GLCM classification method'''

from LungSegmentation.LungSegmentation_MethodKMeans_AllTypes import *
pi = np.pi
class Matrix:
    '''this class contains methods to create glcm matrix from pixels array and get its properties'''
    image_array = None
    def __init__(self, image_array):
        self.image_array = image_array.astype(np.uint8)

    def GetMatrix(self,distances=[5],angles=[0,pi/4,pi/2,3*pi/4]):
        return ft.greycomatrix(self.image_array,distances,angles)
    
    def GetMatrixPatch(self,patch,distances,angles):
        return ft.greycomatrix(patch,distances,angles)

    def GetPropsFromMatrix(self):
        mtrx = self.GetMatrix()
        props = []
        for c in list(ft.greycoprops(mtrx,prop='contrast')):
            for i in c:
                props.append(i) 
        for c in list(ft.greycoprops(mtrx,prop='correlation')):
            for i in c:
                props.append(i) 
        for c in list(ft.greycoprops(mtrx,prop='energy')):
            for i in c:
                props.append(i)  
        for c in list(ft.greycoprops(mtrx,prop='homogeneity')):
            for i in c:
                props.append(i) 
        return props

class Model:
    '''this class contains SVM SVC model and implements basic model functionalities as well as label generation method for train data'''
    model = None
    def __init__(self):
        self.model = svm.SVC()
    
    def FitModel(self,data,labels):
        self.model.fit(data,labels)
    
    def PredictModel(self,data):
        return self.model.predict(data)

    def CrossValidate(self,data,labels,cv=5):
        return cross_val_score(self.model,data,labels,cv=cv)

    @staticmethod    
    def GetLabels():
        labels = []
        for i in range(50):
            labels.append('covid')
        for i in range(50):
            labels.append('normal')
        return labels
    

class ImageEnsemble:
    '''this class hold a collection of dicom images as well as their respective segmented lungs'''
    folders = None
    dicoms = None
    lungs = None
    matrices = None
    props = None
    def __init__(self,folders=None,gotFolders=False):
        if(gotFolders):
            self.folders = folders
    
    def MakeDicoms(self,single_folder=None,single_file=None):
        if(self.folders is None and single_file is not None):
            self.dicoms=[]
            self.dicoms.append(DicomImage(single_folder,single_file))
        else:
            self.dicoms=[]
            for folder in self.folders:
                for fl in os.listdir(folder):
                    self.dicoms.append(DicomImage(folder,fl))

    def GetLungs(self):
        self.lungs = []
        for dcm in self.dicoms:
            self.lungs.append(make_lungmask(dcm.get_current_slice()))
        

    def GetMatrices(self):
        self.matrices=[]
        for lung in self.lungs:
            self.matrices.append(Matrix(lung))
    
    def GetProps(self):
        self.props=[]
        for array in self.matrices:
            self.props.append(array.GetPropsFromMatrix())
            

    


stime = time.time()
flds = [os.path.join(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs")]
e = ImageEnsemble(flds,gotFolders=True)
e.MakeDicoms()
e.GetLungs()
e.GetMatrices()
e.GetProps()
print(len(e.props))
print(len(e.props[0]))
print(len(e.props[1]))
print(e.props[0])
print('Making matrices - execution time: ',time.time()-stime)
# print(len(e.props)," ",len(e.props[0])," ",len(e.props[0][0]))

model = Model()
labels = model.GetLabels()
model.FitModel(e.props,labels)
print('Making matrices + 5-fold x validation - execution time: ',time.time()-stime)

dump(model.model, 'glcmModelFitFinal.joblib') 
plt.imshow(l[0][65],cmap='gray')
plt.show()



    
