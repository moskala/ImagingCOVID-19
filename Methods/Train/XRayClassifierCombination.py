from ClassifierCombination import *

# glcm
# flds = [os.path.join(r"C:\Users\Maya\studia\4rok\inz\covidSeg\Train\Train - big",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\covidSeg\Train\Train - big")]
# e = ImageEnsemble(gotFolders=False)
# for fld in flds:
#     for fl in os.listdir(fld):
#         if(fl.__contains__('.png')):
#             io = XRayPngImage(fld,fl)
#         else:
#             io = XRayJpgImage(fld,fl)
#         e.MakeImage(io,0)
#         print('image added')

# dump(e,'imageEnsemble.joblib')
e = load('imageEnsemble.joblib')

# #e.MakeDicoms()
# # e.GetLungsXray()
e.GetMatrices()
e.GetProps()
glcmFts = e.props
# # # #dump(glcmFts,'glcmFeatures.joblib')
print('glcm done')

# # # # alex
# # alex = Alex(load('featureExtraction.joblib'))
# # alexFts = alex.GetFeaturesFromList(e.lungs)
# # alexFts = alex.ChangeDimAndStandardize(alexFts)
# # alexFts = alex.DoPCA(alexFts,n=50)
# # # dump(alexFts,'alexFeatures.joblib')
# # print('alex done')
# # # #haralick
# # # e = ImageEnsemble([os.path.join(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs")],gotFolders=True)
# # # e.MakeDicoms()
# # # e.GetLungs()
h = Haralick(e.lungs)
haralickFts = h.GetHaralickFtsAll()
# # dump(np.hstack((haralickFts,glcmFts)),'glcmHaralickFeatures.joblib')
print('haralick done')
# glcm
# flds = [os.path.join(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs")]
# e = ImageEnsemble(flds,gotFolders=True)
# e.MakeDicoms()
# e.GetLungs()
# e.GetMatrices()
# e.GetProps()
# glcmFts = e.props

# #print(glcmFts)
# #haralick
# e = ImageEnsemble([os.path.join(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs",fold) for fold in os.listdir(r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs")],gotFolders=True)
# e.MakeDicoms()
# e.GetLungs()
# h = Haralick(e.lungs)
# haralickFts = h.GetHaralickFtsAll()
##dump(np.hstack((haralickFts,glcmFts)),'glcmHaralickData.joblib')

# making model linear discirminant glcm+haralick
# cc = ClassifierCombination()
# cc.make_array2(haralickFts,glcmFts)
# cc.get_labels()
# cc.FitModelLinearDiscriminant()
# dump(cc.svm.modelLinearDicriminant,'glcmHaralickLinearDiscriminant.joblib')

# # making model linear discirminant glcm+haralick
# cc = ClassifierCombination()
# gh = load('glcmHaralickFeatures.joblib')
# cc.make_array1(gh)
# cc.get_labels_xray()
# cc.fit()
# dump(cc.svm.model,'glcmHaralickSvmLinear.joblib')

# # making model linear discirminant alexnet
# cc = ClassifierCombination()
# alexFts = load('alexFeatures.joblib')
# cc.make_array1(alexFts)
# cc.get_labels_xray()
# cc.fit()
# dump(cc.svm.model,'alexneSvmLinear.joblib')

# cc = ClassifierCombination()
# cc.make_array1(load('glcmHaralickFeatures.joblib'))
# cc.get_labels_xray()

# print('glcm+haralick - linear discriminant',cc.cross_validateLD(cv=7))

# print(haralickFts)
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

# combination glcm+haralick, random forest
# cc = ClassifierCombination()
# cc.make_array2(haralickFts,glcmFts)
# cc.get_labels()
# print('glcm+haralick - random forest ',cc.cross_validateRF(cv=7))

# combination glcm+haralick, linear discriminant
# cc = ClassifierCombination()
# cc.make_array2(haralickFts,glcmFts)
# cc.get_labels()

# print('glcm+haralick - linear discriminant',cc.cross_validateLD(cv=7))

# combination alexnet, linear discriminant
# cc = ClassifierCombination()
# cc.make_array1(alexFts)
# cc.get_labels()
# print('alexnet - linear discriminant',cc.cross_validateLD(cv=7))

# # combination alexnet, random forest
# cc = ClassifierCombination()
# cc.make_array1(alexFts)
# cc.get_labels()
# print('alexnet - random forest ',cc.cross_validateRF(cv=7))

# combination alexnet, logistic regression
# cc = ClassifierCombination()
# cc.make_array1(alexFts)
# cc.get_labels()
# print('alexnet - logistic regression ',cc.cross_validateLR(cv=7))

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


# # combination haralick+glcm, kernel rbf
# cc2 = ClassifierCombination()
# cc2.make_array2(haralickFts,glcmFts)
# cc2.get_labels()
# cc2.fit()
# dump(cc2.svm.model,'glcmHaralickSvmRbf.joblib')
# print('haralick+glcm',cc2.cross_validate(cv=7))

# # combination haralick+glcm, kernel linear
# cc2 = ClassifierCombination(kernel='linear')
# cc2.make_array2(haralickFts,glcmFts)
# cc2.get_labels()
# cc2.fit()
# dump(cc2.svm.model,'glcmHaralickSvmLinear.joblib')

# # combination alexnet, kernel linear
# cc3 = ClassifierCombination(kernel='linear')
# cc3.make_array1(alexFts)
# cc3.get_labels()
# cc3.fit()
# dump(cc3.svm.model,'alexnetSvmLinear.joblib')
# print('alexnet',cc3.cross_validate(cv=7))

# combination glcm, kernel linear
# cc4 = ClassifierCombination()
# cc4.make_array1(glcmFts)
# cc4.get_labels()
# print('glcm',cc4.cross_validate(cv=7))

# # combination haralick, kernel linear
# cc5 = ClassifierCombination()
# cc5.make_array1(haralickFts)
# cc5.get_labels()
# print('haralick',cc5.cross_validate(cv=7))


# final model evaluation - xray


cc = ClassifierCombination()
cc.make_array2(haralickFts, glcmFts)
cc.get_labels_xray()
print(cc.array)
print(cc.labels)
tn, fp, fn, tp = cc.cross_evaluate(cv=10)
print(cc.get_measures(tp, tn, fp, fn))
