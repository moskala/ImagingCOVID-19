import pickle
from joblib import dump, load
import sys,os
from pathlib import Path
from glcm import *

# model = load('glcmModelFitFinal.joblib') 

# e = ImageEnsemble([r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\csTest"])
# e.MakeDicoms()
# e.GetLungs()
# e.GetMatrices()
# e.GetProps()

# print(model.predict(e.props))

def PredictGLCM(folder,file,model_path):
    model = load(model_path) 
    e = ImageEnsemble()
    e.MakeDicoms(folder,file)
    e.GetLungs()
    e.GetMatrices()
    e.GetProps()
    return model.predict(e.props[0].reshape(1,-1))



