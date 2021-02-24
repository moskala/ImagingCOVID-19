from Glcm import *
import mahotas
# import torch
# import torchvision.transforms as transforms
# from PIL import Image
# import Grayscale as gray
# from sklearn.decomposition import PCA
# from sklearn.preprocessing import StandardScaler
# from joblib import dump, load
# import numpy as np
# import os
# import glob
# from sklearn import svm
# from sklearn import metrics

class Haralick:
    lungs_list = None

    def __init__(self, lungs=None):
        self.lungs_list = lungs

    def GetHaralickFts(self, image):
        return mahotas.features.haralick(image).flatten()

    def GetHaralickFtsAll(self):
        hrl = []
        for lung in self.lungs_list:
            hrl.append(self.GetHaralickFts(lung))
        return hrl
