from Glcm import *
from Alexnet import *
from Haralick import *
import numpy as np
from ImageMedical.XRayImageClass import *
from ImageMedical.CTImageClass import *


class ClassifierCombination:
    svm = None
    array = None
    labels = None

    def __init__(self, model=None, kernel='rbf'):
        if model is None:
            self.svm = Model(kernel)
        else:
            self.svm = model

    def make_array3(self, glcm, haralick, alex):
        self.array = np.hstack((glcm, haralick, alex))

    def make_array2(self, glcm, alex):
        self.array = np.hstack((glcm, alex))

    def make_array1(self, alex):
        self.array = alex

    def get_labels(self):
        normal_labels = ['normal'] * 600
        covid_labels = ['covid'] * 600
        self.labels = normal_labels + covid_labels

    def get_labels_xray(self):
        labels = []
        for i in range(204):
            labels.append('covid')
        for i in range(210):
            labels.append('normal')
        self.labels = labels

    def get_measures(self, tp, tn, fp, fn):
        sen = tp / (tp + fn) * 100
        spe = tn / (fp + tn) * 100
        ppv = tp / (tp + fp) * 100
        npv = tn / (tn + fn) * 100
        acc = (tp + tn) / (tp + fn + tn + fp) * 100
        mcc = (tp * tn - fp * fn) / math.sqrt((tp + fn) * (tp + fp) * (tn + fp) * (tn + fn))
        return sen, spe, ppv, npv, acc, mcc

    def fit(self):
        return self.svm.FitModel(self.array, self.labels)

    def FitModelLinearDiscriminant(self):
        return self.svm.FitModelLinearDiscriminant(self.array,self.labels)
    
    def cross_evaluate(self, cv=5):
        return self.svm.GetModelEvaluation(self.array, self.labels, cv=cv)

    def cross_evaluateLD(self, cv=5):
        return self.svm.GetModelEvaluationLD(self.array, self.labels, cv=cv)

    def cross_evaluateLR(self, cv=5):
        return self.svm.GetModelEvaluationLR(self.array, self.labels, cv=cv)

    def cross_evaluateRF(self, cv=5):
        return self.svm.GetModelEvaluationRF(self.array, self.labels, cv=cv)

    def cross_validate(self, cv):
        return self.svm.CrossValidate(self.array, self.labels, cv=cv)

    def cross_validateRF(self, cv):
        return self.svm.CrossValidateRandomForest(self.array, self.labels, cv=cv)

    def cross_validateLR(self, cv):
        return self.svm.CrossValidateLogisticRegression(self.array, self.labels, cv=cv)

    def cross_validateLD(self, cv):
        return self.svm.CrossValidateLinearDiscriminant(self.array, self.labels, cv=cv)

