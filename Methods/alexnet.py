#from alexnet_pytorch import AlexNet #- to trzeba tylko raz uruchomic?
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

class Alex:
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
    
    def DoPCA(self,features,n=100):
        pca = PCA(n_components=n)
        pcafts=[]
        for ft in features:
            pcaM=[]
            for matrix in ft:
                for row in matrix:
                    for col in row:
                        pcaM.append(col)
                #t = pca.fit_transform(matrix.reshape(1,-1))
            pcafts.append(pcaM)
        # print(len(pcafts))
        # for p in pcafts:
        #     print(len(p))
        pcafts = pca.fit_transform(pcafts)
        return pcafts


# start = time.time()
# e = ImageEnsemble(os.path.join(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs"))
# e.MakeDicoms()
# e.GetLungs()

# alex = Alex()
# fts = alex.GetFeaturesFromList(e.lungs)

# # standaryzacja
# newfts=alex.ChangeDimAndStandardize(fts)
# pcafts = alex.DoPCA(newfts)
# print(pcafts)

# # svm
# svm = Model()
# labels = svm.GetLabels()

# svm.FitModel(pcafts,labels)
# dump(svm.model, 'alexnetModel.joblib') 
# print(scores)

# #print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

# print("Execution time: ",time.time()-start)