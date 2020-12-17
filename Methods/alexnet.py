from alexnet_pytorch import AlexNet #- to trzeba tylko raz uruchomic?
from glcm import *
import torch
from glcm import *
import torchvision.transforms as transforms
#alex2 = AlexNet.from_pretrained('alexnet')
from PIL import Image
import Grayscale as gray
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
import math
import numpy as np

class Alex:
    '''this class uses pytorch pretrained alexnet to extract deep features from pixel arrays'''
    alex = None
    def __init__(self,model=None):
        if(model is None):
            self.alex = AlexNet.from_pretrained('alexnet', num_classes=2)
        else:
            self.alex = model
    
    def GetFeatures(self,image):
        preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        im = Image.fromarray(gray.convert_array_to_grayscale(image))
        tensor = preprocess(im.convert('RGB')).unsqueeze(0)
        return self.alex.extract_features(tensor)

    def GetFeaturesFromList(self,lungList):
        lis = []
        for image in lungList:
            lis.append(self.GetFeatures(image))
        return lis

    def ChangeDimAndStandardize(self,features,isTensor = True):
        # standaryzacja
        newfts=[]
        for ft in features:
            newM=[]
            if(isTensor):
                ft = ft.squeeze().detach().numpy()
            else:
                ft = ft.detach().numpy()
            for matrix in ft:
                newM.append(StandardScaler().fit_transform(matrix))
            newfts.append(newM)
        return newfts
    
    def DoPCA(self,features,n=50):
        pca = PCA(n_components=n)
        mn = math.inf
        mx=-math.inf
        pcafts=[]
        for ft in features:
            pcaM=[]
            for matrix in ft:
                for row in matrix:
                    for col in row:
                        pcaM.append(col)
                        if(col>mx):
                            mx=col
                        if(col<mn):
                            mn=col
            pcafts.append(pcaM)
        pcafts = pca.fit_transform(pcafts)
        return pcafts

# 10

# start = time.time()
# e = ImageEnsemble([r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\csTest"],gotFolders=True)
# e.MakeDicoms()
# e.GetLungs()



# alex = Alex()
# fts = alex.GetFeaturesFromList(e.lungs)
# first = fts[0].squeeze(0).detach().numpy()
# dets = []
# for matrix in first:
#     dets.append(np.linalg.det(matrix))
# print(dets)
# wszystkie

# start = time.time()
# e = ImageEnsemble([os.path.join(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs")],gotFolders=True)
# e.MakeDicoms()
# e.GetLungs()

# alex = Alex()
# fts = alex.GetFeaturesFromList(e.lungs)



# # standaryzacja
# newfts=alex.ChangeDimAndStandardize(fts)
# dump(newfts,'csPrePCAFeatures50.joblib')
# # pcafts = alex.DoPCA(newfts)
# print(pcafts)

# # svm
# svm = Model()
# labels = svm.GetLabels()

# svm.FitModel(pcafts,labels)
# dump(svm.model, 'alexnetModel.joblib') 
# print(scores)

# #print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

# print("Execution time: ",time.time()-start)