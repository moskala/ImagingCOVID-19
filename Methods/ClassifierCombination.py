from Glcm import *
from Alexnet import *
from Haralick import *
import numpy as np


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
        covid_labels = ['covid'] * 600
        normal_labels = ['normal'] * 600
        self.labels = covid_labels + normal_labels

    def get_labels_xray(self):
        labels = []
        for i in range(204):
            labels.append('covid')
        for i in range(210):
            labels.append('normal')
        self.labels = labels

    def fit(self):
        return self.svm.FitModel(self.array, self.labels)

    def FitModelLinearDiscriminant(self):
        return self.svm.FitModelLinearDiscriminant(self.array, self.labels)

    def cross_validate(self, cv):
        return self.svm.CrossValidate(self.array, self.labels, cv=cv)

    def cross_validateRF(self, cv):
        return self.svm.CrossValidateRandomForest(self.array, self.labels, cv=cv)

    def cross_validateLR(self, cv):
        return self.svm.CrossValidateLogisticRegression(self.array, self.labels, cv=cv)

    def cross_validateLD(self, cv):
        return self.svm.CrossValidateLinearDiscriminant(self.array, self.labels, cv=cv)
