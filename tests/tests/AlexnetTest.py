import pickle
from joblib import dump, load
import sys,os
from pathlib import Path
sys.path.append(str(Path().resolve().parent))
from Glcm import *
from Alexnet import Alex

from Glcm import *

# model = load('glcmModelFitFinal.joblib') 

# e = ImageEnsemble([r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\csTest"])
# e.MakeDicoms()
# e.GetLungs()
# e.GetMatrices()
# e.GetProps()

# print(model.predict(e.props))

data_folder = r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs"#w srodku 10 roznych ct po 10 dcm
test_folder = r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\csTest" #w srodku 1 dcm

start = time.time()
dcms = []
dcms.append(test_folder)

e = ImageEnsemble(dcms)
e.MakeDicoms()
e.GetLungs()

alex = Alex(load('featureExtraction.joblib'))
testft = alex.GetFeatures(e.lungs[0])
print(testft.size())
print("przed change dim")
print(len(testft))
print(len(testft[0]))
testft = alex.ChangeDimAndStandardize(testft,isTensor=False)
print("po change dim")
print(len(testft))
print(len(testft[0]))
newfts = load('csPrePCAFeatures.joblib')
print("zaladowane macierze")
print(len(newfts))
print(len(newfts[0]))
newfts.append(testft[0])
print(len(newfts))
print(len(newfts[0]))
pcafts = alex.DoPCA(newfts)
print("po pca")
print(len(pcafts))
print(len(pcafts[0]))

# print(len(pcafts))
model=load('alexnetModel.joblib')
print(model.predict(pcafts[100].reshape(1, -1)))
print("Execution time: ",time.time()-start)