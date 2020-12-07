import pickle
from joblib import dump, load
import sys,os
from pathlib import Path
sys.path.append(str(Path().resolve().parent))
from glcm import *

model = load('glcmModelFitFinal.joblib') 

e = ImageEnsemble([r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\csTest"])
e.MakeDicoms()
e.GetLungs()
e.GetMatrices()
e.GetProps()

print(model.predict(e.props))





