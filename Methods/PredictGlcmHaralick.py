import pickle
from joblib import dump, load
import sys,os
from pathlib import Path
from haralick import *
from glcm import *
import numpy as np

def PredictGlcmHaralick(image_object,model_path,train_data,isPretrained=True):
    if(isPretrained):
        model = load(model_path) 
    else:
        model=model_path 
        model.fit(load(train_data),Model.GetLabels())
    e = ImageEnsemble()
    e.MakeImage(image_object)
    e.GetLungs()
    h = Haralick()
    fts = h.GetHaralickFts(e.lungs[0])
    e.GetMatrices()
    e.GetProps()
    stck = np.hstack((fts,e.props[0]))
    print(fts)
    print(e.props)
    return model.predict(stck.reshape(1, -1)),model