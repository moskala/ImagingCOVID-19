from glcm import *
from alexnet import *
from haralick import *
import numpy as np

class ClassifierCombination():
    svm = None
    array = None
    labels = None
    def __init__(self,model = None):
        if(model is None):
            self.svm = Model()
        else:
            self.svm = model

    def make_array3(self,glcm,haralick,alex):
        self.array = np.hstack((glcm,haralick,alex))

    def make_array2(self,glcm,alex):
        self.array = np.hstack((glcm,alex))
    
    def make_array1(self,alex):
        self.array = alex

    def get_labels(self):
        self.labels= Model.GetLabels()

    def fit(self):
        return self.svm.FitModel(self.array,self.labels)
    
    def cross_validate(self,cv):
        return self.svm.CrossValidate(self.array,self.labels,cv=cv)

    

# alex
alex = Alex(load('featureExtraction.joblib'))
alexFts = load('csPrePCAFeatures50.joblib')
alexFts = alex.DoPCA(alexFts,n=50)

# glcm
flds = [os.path.join(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs")]
e = ImageEnsemble(flds,gotFolders=True)
e.MakeDicoms()
e.GetLungs()
e.GetMatrices()
e.GetProps()
glcmFts = e.props

#haralick
e = ImageEnsemble([os.path.join(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs")],gotFolders=True)
e.MakeDicoms()
e.GetLungs()
h = Haralick(e.lungs)
haralickFts = h.GetHaralickFtsAll()

# kernel linear
# combibation all 3, kernel linear
# cc = ClassifierCombination()
# cc.make_array3(glcmFts,haralickFts,alexFts)
# cc.get_labels()
# print(cc.cross_validate(cv=7))
# [1.         0.86666667 1.         1.         1.         1.
# 1.        ]
# kernel default 
# [0.7  0.8  1.   1.   0.95]

# combination glcm+alexnet, kernel linear
# cc = ClassifierCombination()
# cc.make_array2(glcmFts,alexFts)
# cc.get_labels()
# print('glcm+alexnet ',cc.cross_validate(cv=7))

# # combination haralick+alexnet, kernel linear
# cc1 = ClassifierCombination()
# cc1.make_array2(haralickFts,alexFts)
# cc1.get_labels()
# print('haralick+alexnet',cc1.cross_validate(cv=7))


# # combination haralick+glcm, kernel linear
# cc2 = ClassifierCombination()
# cc2.make_array2(haralickFts,glcmFts)
# cc2.get_labels()
# print('haralick+glcm',cc2.cross_validate(cv=7))


# # combination alexnet, kernel linear
# cc3 = ClassifierCombination()
# cc3.make_array1(alexFts)
# cc3.get_labels()
# print('alexnet',cc3.cross_validate(cv=7))

# combination glcm, kernel linear
cc4 = ClassifierCombination()
cc4.make_array1(glcmFts)
cc4.get_labels()
print('glcm',cc4.cross_validate(cv=7))

# combination haralick, kernel linear
cc5 = ClassifierCombination()
cc5.make_array1(haralickFts)
cc5.get_labels()
print('haralick',cc5.cross_validate(cv=7))