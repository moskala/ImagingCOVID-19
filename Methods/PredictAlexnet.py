import pickle
from joblib import dump, load
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from Glcm import *
from Alexnet import Alex
import math
from ExaminationType import ExaminationType


def PredictAlex(image_object, index, modelAlex, features, classifier, examination_type=ExaminationType.CT,
                isPretrained=True):
    """this function is used by gui when button "Alexnet" is clicked"""

    e = ImageEnsemble()
    e.MakeImage(image_object, index)
    alex = Alex(load(modelAlex))
    testft = alex.GetFeatures(e.lungs[0])
    testft = alex.ChangeDimAndStandardize(testft, isTensor=False)
    newfts = load(features)
    newfts.append(testft[0])
    pcafts = alex.DoPCA(newfts)

    if isPretrained:
        model = load(classifier)
    else:
        model = classifier

    if examination_type is ExaminationType.XRAY:
        model.fit(pcafts[0:len(pcafts) - 1], Model.GetLabelsXray())
    else:
        model.fit(pcafts[0:len(pcafts) - 1], Model.GetLabels())
    test = pcafts[len(pcafts) - 1].reshape(1, -1)

    return model.predict(test), model
