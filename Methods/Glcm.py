'''this script contains classes necessary to implement GLCM classification method'''
from skimage.feature import texture as ft
import sys
import os
from sklearn import svm
from pathlib import Path
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
from Grayscale import *
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'ImageMedical')))
from ImageClass import *
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'LungSegmentation')))
from MethodKMeans import *
import MethodUNetXRay as Xray

pi = np.pi


class Matrix:
    """this class contains methods to create glcm matrix from pixels array and get its properties"""

    image_array = None

    def __init__(self, image_array):
        self.image_array = image_array.astype(np.uint8)

    def GetMatrix(self, distances=[5], angles=[0, pi / 4, pi / 2, 3 * pi / 4]):
        return ft.greycomatrix(self.image_array, distances, angles)

    def GetMatrixPatch(self, patch, distances, angles):
        return ft.greycomatrix(patch, distances, angles)

    def GetPropsFromMatrix(self):
        mtrx = self.GetMatrix()
        props = []
        for c in list(ft.greycoprops(mtrx, prop='contrast')):
            for i in c:
                props.append(i)
        for c in list(ft.greycoprops(mtrx, prop='correlation')):
            for i in c:
                props.append(i)
        for c in list(ft.greycoprops(mtrx, prop='energy')):
            for i in c:
                props.append(i)
        for c in list(ft.greycoprops(mtrx, prop='homogeneity')):
            for i in c:
                props.append(i)
        return props


class Model:
    """this class contains SVM SVC model and implements basic model functionalities
    as well as label generation method for train data"""

    model = None
    modelRandomForest = None
    modelLinearDicriminant = None
    modelLogisticRegression = None

    def __init__(self, kernel='rbf', max_features='auto', solver='liblinear'):
        self.model = svm.SVC(kernel='linear')  # linear
        self.modelRandomForest = RandomForestClassifier(max_features='sqrt')    # max_features
        self.modelLogisticRegression = LogisticRegression(max_iter=10000, solver='saga')    # solver
        self.modelLinearDicriminant = LinearDiscriminantAnalysis(solver='svd')   # lsqr, shrinkage='auto'

    def FitModel(self,data,labels):
        self.model.fit(data,labels)

    def FitModelRandomForest(self, data, labels):
        self.modelRandomForest.fit(data, labels)

    def FitModelLogisticRegression(self, data, labels):
        self.modelLogisticRegression.fit(data, labels)

    def FitModelLinearDiscriminant(self, data, labels):
        self.modelLinearDicriminant.fit(data, labels)

    def PredictModel(self, data):
        return self.model.predict(data)

    def PredictModelRandomForest(self, data):
        return self.modelRandomForest.predict(data)

    def PredictModelLogisticRegression(self, data):
        return self.modelLogisticRegression.predict(data)

    def PredictModelLinearDiscriminant(self, data):
        return self.modelLinearDicriminant.predict(data)

    def GetModelEvaluation(self,data,labels,cv=5):
        labels_pred = cross_val_predict(self.model, data, labels, cv=cv)
        tn, fp, fn, tp = confusion_matrix(labels, labels_pred,labels=['normal','covid']).ravel()
        return tn, fp, fn, tp

    def GetModelEvaluationLR(self,data,labels,cv=5):
        labels_pred = cross_val_predict(self.modelLogisticRegression, data, labels, cv=cv)
        tn, fp, fn, tp = confusion_matrix(labels, labels_pred,labels=['normal','covid']).ravel()
        return tn, fp, fn, tp

    def GetModelEvaluationRF(self,data,labels,cv=5):
        labels_pred = cross_val_predict(self.modelRandomForest, data, labels, cv=cv)
        tn, fp, fn, tp = confusion_matrix(labels, labels_pred,labels=['normal','covid']).ravel()
        return tn, fp, fn, tp

    def GetModelEvaluationLD(self,data,labels,cv=5):
        labels_pred = cross_val_predict(self.modelLinearDicriminant, data, labels, cv=cv)
        tn, fp, fn, tp = confusion_matrix(labels, labels_pred ,labels=['normal','covid']).ravel()
        return tn, fp, fn, tp

    def CrossValidate(self,data,labels,scoring='accuracy',cv=5):
        return cross_val_score(self.model,data,labels,cv=cv)

    def CrossValidateRandomForest(self,data,labels,scoring=['accuracy', 'precision','recall','f1'],cv=5):
        return cross_val_score(self.modelRandomForest,data,labels,scoring,cv=cv)

    def CrossValidateLogisticRegression(self,data,labels,scoring=['accuracy', 'precision','recall','f1'],cv=5):
        return cross_val_score(self.modelRandomForest,data,labels,scoring,cv=cv)

    def CrossValidateLinearDiscriminant(self,data,labels,scoring=['accuracy', 'precision','recall','f1'],cv=5):
        return cross_val_score(self.modelLinearDicriminant,data,labels,scoring,cv=cv)

    @staticmethod
    def GetLabels():
        normal_labels = ['normal'] * 600
        covid_labels = ['covid'] * 600
        labels = normal_labels + covid_labels
        return labels

    @staticmethod
    def GetLabelsXray():
        labels = []
        for i in range(204):
            labels.append('covid')
        for i in range(210):
            labels.append('normal')
        return labels


class ImageEnsemble:
    """this class hold a collection of dicom images as well as their respective segmented lungs"""

    folders = None
    dicoms = None
    lungs = None
    matrices = None
    props = None

    def __init__(self, folders=None, gotFolders=False):
        self.lungs = []
        if gotFolders:
            self.folders = folders
    
    def MakeDicoms(self,single_folder=None,single_file=None):
        if self.folders is None and single_file is not None:
            self.dicoms=[]
            self.dicoms.append(DicomImage(single_folder, single_file))
        else:
            self.dicoms = []
            for folder in self.folders:
                for fl in os.listdir(folder):
                    self.dicoms.append(DicomImage(folder, fl))

    
    def MakeImage(self,image_object,index):
        image_object.get_next_slice(index)
        print('image object slice: ',image_object.current_slice_number)
        lungs = image_object.get_segmented_lungs()
        self.lungs.append(lungs)

    def GetLungsXray(self):
        self.lungs = []
        for fld in self.folders:
            s, m = Xray.make_lungmask_multiple(os.listdir(fld), fld)
            gs = []
            for a in s:
                gs.append(convert_array_to_grayscale(a))
            self.lungs.extend(gs)

    def GetMatrices(self):
        self.matrices = []
        for lung in self.lungs:
            self.matrices.append(Matrix(lung))

    def GetProps(self):
        self.props = []
        for array in self.matrices:
            self.props.append(array.GetPropsFromMatrix())
