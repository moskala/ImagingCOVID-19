import pickle
from joblib import dump, load
import sys, os
from pathlib import Path
from Haralick import *
from Glcm import *
import numpy as np
from ExaminationType import ExaminationType


def PredictGlcmHaralick(image_object, index, model_path, train_data, examination_type=ExaminationType.CT,
                        isPretrained=True):
    if isPretrained:
        model = load(model_path)
    else:
        model = model_path
        if examination_type is ExaminationType.XRAY:
            model.fit(load(train_data), Model.GetLabelsXray())
        else:
            model.fit(load(train_data), Model.GetLabels())
    e = ImageEnsemble()
    e.MakeImage(image_object, index)
    h = Haralick()
    fts = h.GetHaralickFts(e.lungs[0])
    e.GetMatrices()
    e.GetProps()
    stck = np.hstack((fts, e.props[0]))
    return model.predict(stck.reshape(1, -1)), model
