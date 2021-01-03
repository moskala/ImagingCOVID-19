from glcm import *
import torch
from glcm import *
import torchvision.transforms as transforms
from PIL import Image
import Grayscale as gray
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
import numpy as np
import os
import glob
import mahotas
from sklearn import svm

from sklearn import metrics

class Haralick():
    lungs_list = None
    def __init__(self,lungs=None):
        self.lungs_list = lungs
    def GetHaralickFts(self,image):
        return mahotas.features.haralick(image).flatten()
    def GetHaralickFtsAll(self):
        hrl = []
        for lung in self.lungs_list:
            hrl.append(self.GetHaralickFts(lung))
        return hrl

# # e = ImageEnsemble([os.path.join(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs")],gotFolders=True)
# # e.MakeDicoms()
# # e.GetLungs()
# # h = Haralick(e.lungs)
# # fts = h.GetHaralickFtsAll()


# modelH = Model()
# labels = modelH.GetLabels()
# print(modelH.CrossValidate(fts,labels,cv=7))

# modelH.FitModel(fts,labels)
# dump(modelH,'haralickSVM.joblib')

# # do testow
# test = ImageEnsemble([r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\csTest"],gotFolders= True)
# test.MakeDicoms()
# test.GetLungs()
# hTest = Haralick(test.lungs)
# ftsTest = modelH.PredictModel(hTest.GetHaralickFtsAll())

# y_pred = []
# for i in range(11):
#     y_pred.append('normal')
# for i in range(9):
#     y_pred.append('covid')

# print("Accuracy:",metrics.accuracy_score( y_pred,ftsTest))
# # Model Precision: what percentage of positive tuples are labeled as such?

# print("Precision:",metrics.precision_score(np.array(y_pred),ftsTest,pos_label='covid'))

# # Model Recall: what percentage of positive tuples are labelled as such?
# print("Recall:",metrics.recall_score(np.array(y_pred),ftsTest,pos_label='covid'))
