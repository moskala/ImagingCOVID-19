import mahotas
from Glcm import *


class Haralick:
    lungs_list = None

    def __init__(self, lungs=None):
        self.lungs_list = lungs

    def GetHaralickFts(self, image):
        return mahotas.features.haralick(image).flatten()

    def GetHaralickFtsAll(self):
        hrl = []
        for lung in self.lungs_list:
            hrl.append(self.GetHaralickFts(lung))
        return hrl
