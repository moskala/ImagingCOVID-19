import pickle
from joblib import dump, load
import sys,os
from pathlib import Path
sys.path.append(str(Path().resolve().parent))
from glcm import *

'''this script tests glcm model prediction for exemplary folder'''

model = load('glcmModelFitFinal.joblib') 

e = ImageEnsemble([r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\csTest"],gotFolders=True)
e.MakeDicoms()
e.GetLungs()
e.GetMatrices()
e.GetProps()

print(model.predict(e.props))





