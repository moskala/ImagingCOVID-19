import pickle
from joblib import dump, load
import sys,os
from pathlib import Path
from haralick import *

def PredictHaralick(folder,file,model_path):
    model = load(model_path) 
    e = ImageEnsemble()
    e.MakeDicoms(folder,file)
    e.GetLungs()
    h = Haralick()
    fts = h.GetHaralickFts(e.lungs[0])
    return model.model.predict(fts.reshape(1, -1))
