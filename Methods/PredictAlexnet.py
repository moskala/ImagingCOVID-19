import pickle
from joblib import dump, load
import sys,os
from pathlib import Path
sys.path.append(str(Path().resolve().parent))
from glcm import *
from alexnet import Alex

def PredictAlex(folder,fil,modelAlex,features,svm):
    e = ImageEnsemble()
    e.MakeDicoms(folder,fil)
    e.GetLungs()
    alex = Alex(load(modelAlex))
    testft = alex.GetFeatures(e.lungs[0])
    testft = alex.ChangeDimAndStandardize(testft,isTensor=False)
    newfts = load(features)
    newfts.append(testft[0])
    pcafts = alex.DoPCA(newfts)
    model=load(svm)
    return model.predict(pcafts[len(pcafts)-1].reshape(1, -1))
    
