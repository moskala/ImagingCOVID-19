import pickle
from joblib import dump, load
import sys
import os
from pathlib import Path
from Haralick import Haralick
from Glcm import ImageEnsemble


def PredictHaralick(folder, file, model_path):
    model = load(model_path)
    e = ImageEnsemble()
    e.MakeDicoms(folder, file)
    e.GetLungs()
    h = Haralick()
    fts = h.GetHaralickFts(e.lungs[0])
    return model.predict(fts.reshape(1, -1))
