import pickle
from joblib import dump, load
import sys,os
from pathlib import Path
sys.path.append(str(Path().resolve().parent))
from glcm import *
from alexnet import Alex
import math

def PredictAlex(image_object,modelAlex,features,classifier,isPretrained=True):
    '''this function is used by gui when button "Alexnet" is clicked'''
    e = ImageEnsemble()
    e.MakeImage(image_object)
    e.GetLungs()
    alex = Alex(load(modelAlex))
    testft = alex.GetFeatures(e.lungs[0])
    testft = alex.ChangeDimAndStandardize(testft,isTensor=False)
    newfts = load(features)
    newfts.append(testft[0])
    # print(newfts[len(newfts)-1])
    # print(math.nan in newfts)
    # print(math.inf in newfts)
    pcafts = alex.DoPCA(newfts)
    if(isPretrained):
        model=load(classifier)
    else: 
        model=classifier
    model.fit(pcafts[0:len(pcafts)-1],Model.GetLabels())
    test = pcafts[len(pcafts)-1].reshape(1, -1)
    print(test)
    return model.predict(test),model
    
        

    
