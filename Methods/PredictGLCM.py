import pickle
from joblib import dump, load
import sys, os
from pathlib import Path
from Glcm import *


def PredictGLCM(folder, file, model_path):
    """this function is used by gui when button "GLCM" is clicked"""

    model = load(model_path)
    e = ImageEnsemble()
    e.MakeDicoms(folder, file)
    e.GetLungs()
    e.GetMatrices()
    e.GetProps()
    print(e.props)
    return model.predict(e.props)
