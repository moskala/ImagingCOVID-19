import matplotlib.pyplot as plt
import os
import numpy as np
import sys
from joblib import dump, load
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ClassifierCombination import *
from ImageMedical.CTImageClass import CTNiftiImage
from LungSegmentation.LungSegmentationUtilities import compare_plots


data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', '..', '..',
                                           'data', 'COVID19_1110', 'studies'))

data_folder_ct0 = os.path.join(data_folder, 'CT-0')
data_folder_ct1 = os.path.join(data_folder, 'CT-1')
data_folder_ct2 = os.path.join(data_folder, 'CT-2')
data_folder_ct3 = os.path.join(data_folder, 'CT-3')
data_folder_ct4 = os.path.join(data_folder, 'CT-4')

print(data_folder)
print(data_folder_ct0)

ct0_indexes = list(range(1, 255, 1))
ct1_indexes = list(range(255, 939, 1))
ct2_indexes = list(range(939, 1064, 1))
ct3_indexes = list(range(1064, 1109, 1))
ct4_indexes = list(range(1109, 1110, 1))


def get_study_name(study_id):
    return "study_{0}.nii.gz".format(study_id)

number_of_covid_layers = 0
number_of_normal_layers = 0

e = ImageEnsemble(gotFolders=False)


def append_study(folder, study_name, image_indexes):
    global e
    io = CTNiftiImage(folder, study_name)
    for idx in image_indexes:
        e.MakeImage(io, idx)
        print('total_lungs: {0}'.format(len(e.lungs)))


# NORMAL SET #######################################################################################################

# Study 1
study = get_study_name('0001')
indexes = list(range(17, 28, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 2
study = get_study_name('0002')
indexes = list(range(12, 23, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 3
study = get_study_name('0003')
indexes = list(range(17, 28, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 4
study = get_study_name('0004')
indexes = list(range(20, 31, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 5
study = get_study_name('0005')
indexes = list(range(14, 26, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 6
study = get_study_name('0006')
indexes = list(range(13, 24, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 7
study = get_study_name('0007')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 8
study = get_study_name('0008')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 9
study = get_study_name('0009')
indexes = list(range(27, 38, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 10
study = get_study_name('0010')
indexes = list(range(27, 38, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 11
study = get_study_name('0011')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 12
study = get_study_name('0012')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 13
study = get_study_name('0013')
indexes = list(range(13, 24, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 14
study = get_study_name('0014')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 15
study = get_study_name('0015')
indexes = list(range(12, 23, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 16
study = get_study_name('0016')
indexes = list(range(22, 33, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 17
study = get_study_name('0017')
indexes = list(range(21, 32, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 18
study = get_study_name('0018')
indexes = list(range(21, 32, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 19
study = get_study_name('0019')
indexes = list(range(21, 32, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 20
study = get_study_name('0020')
indexes = list(range(20, 31, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 21
study = get_study_name('0021')
indexes = list(range(18, 24, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 22
study = get_study_name('0022')
indexes = list(range(17, 28, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 23
study = get_study_name('0023')
indexes = list(range(20, 31, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 24
study = get_study_name('0024')
indexes = list(range(17, 30, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 25
study = get_study_name('0025')
indexes = list(range(17, 28, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 26
study = get_study_name('0026')
indexes = list(range(23, 34, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 27
study = get_study_name('0027')
indexes = list(range(13, 25, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 28
study = get_study_name('0028')
indexes = list(range(12, 25, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 29
study = get_study_name('0029')
indexes = list(range(13, 26, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 30
study = get_study_name('0030')
indexes = list(range(17, 28, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 31
study = get_study_name('0031')
indexes = list(range(11, 22, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 32
study = get_study_name('0032')
indexes = list(range(17, 28, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 33
study = get_study_name('0033')
indexes = list(range(17, 28, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 34 - not good

# Study 35
study = get_study_name('0035')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 36
study = get_study_name('0036')
indexes = list(range(17, 28, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 37
study = get_study_name('0037')
indexes = list(range(13, 28, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 38
study = get_study_name('0038')
indexes = list(range(19, 31, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 39
study = get_study_name('0039')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 40
study = get_study_name('0040')
indexes = list(range(16, 27, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 41
study = get_study_name('0041')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 42
study = get_study_name('0042')
indexes = list(range(15, 25, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 43
study = get_study_name('0043')
indexes = list(range(14, 27, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 44
study = get_study_name('0044')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 45
study = get_study_name('0045')
indexes = list(range(15, 26, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 46
study = get_study_name('0046')
indexes = list(range(14, 26, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 47
study = get_study_name('0047')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 48
study = get_study_name('0048')
indexes = list(range(16, 31, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 49
study = get_study_name('0049')
indexes = list(range(21, 31, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 50
study = get_study_name('0050')
indexes = list(range(20, 31, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 51
study = get_study_name('0051')
indexes = list(range(20, 31, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 52
study = get_study_name('0052')
indexes = list(range(15, 26, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 53
study = get_study_name('0053')
indexes = list(range(18, 30, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

# Study 54
study = get_study_name('0054')
indexes = list(range(16, 30, 1))
append_study(data_folder_ct0, study, indexes)
number_of_normal_layers += len(indexes)

print("Normal set done")

# COVID SET ########################################################################################################
#
# SET CT-4

# Study 1110
study = get_study_name('1110')
indexes = list(range(13, 31, 1))
append_study(data_folder_ct4, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1109
study = get_study_name('1109')
indexes = list(range(21, 29, 1))
append_study(data_folder_ct4, study, indexes)
number_of_covid_layers += len(indexes)

# SET CT-3

# Study 1064
study = get_study_name('1064')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1065
study = get_study_name('1065')
indexes = list(range(20, 31, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1066
study = get_study_name('1066')
indexes = list(range(16, 27, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1067
study = get_study_name('1067')
indexes = list(range(15, 29, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1068
study = get_study_name('1068')
indexes = list(range(15, 29, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1069
study = get_study_name('1069')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1070
study = get_study_name('1070')
indexes = list(range(15, 26, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1071
study = get_study_name('1071')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1072
study = get_study_name('1072')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1073
study = get_study_name('1073')
indexes = list(range(16, 27, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1074
study = get_study_name('1074')
indexes = list(range(16, 27, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1075
study = get_study_name('1075')
indexes = list(range(13, 24, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1076
study = get_study_name('1076')
indexes = list(range(13, 24, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1077
study = get_study_name('1077')
indexes = list(range(13, 24, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1078
study = get_study_name('1078')
indexes = list(range(20, 27, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1079
study = get_study_name('1079')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1080
study = get_study_name('1080')
indexes = list(range(16, 27, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1081
study = get_study_name('1081')
indexes = list(range(12, 24, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1082
study = get_study_name('1082')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1083
study = get_study_name('1083')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1084
study = get_study_name('1084')
indexes = list(range(19, 29, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1085
study = get_study_name('1085')
indexes = list(range(16, 28, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1086
study = get_study_name('1086')
indexes = list(range(16, 27, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1087
study = get_study_name('1087')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1088
study = get_study_name('1088')
indexes = list(range(18, 30, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1089
study = get_study_name('1089')
indexes = list(range(14, 26, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1090
study = get_study_name('1090')
indexes = list(range(17, 31, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1091
study = get_study_name('1091')
indexes = list(range(15, 27, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1092
study = get_study_name('1092')
indexes = list(range(14, 24, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1093
study = get_study_name('1093')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1094
study = get_study_name('1094')
indexes = list(range(14, 26, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1095
study = get_study_name('1095')
indexes = list(range(25, 35, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1096
study = get_study_name('1096')
indexes = list(range(19, 29, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1097
study = get_study_name('1097')
indexes = list(range(21, 33, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1098
study = get_study_name('1098')
indexes = list(range(14, 26, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1099
study = get_study_name('1099')
indexes = list(range(22, 32, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1100
study = get_study_name('1100')
indexes = list(range(20, 31, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1101
study = get_study_name('1101')
indexes = list(range(18, 30, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1102
study = get_study_name('1102')
indexes = list(range(21, 36, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1103
study = get_study_name('1103')
indexes = list(range(21, 28, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1104
study = get_study_name('1104')
indexes = list(range(24, 35, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1105
study = get_study_name('1105')
indexes = list(range(24, 36, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1106
study = get_study_name('1106')
indexes = list(range(15, 26, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1107
study = get_study_name('1107')
indexes = list(range(16, 26, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# Study 1108
study = get_study_name('1108')
indexes = list(range(16, 26, 1))
append_study(data_folder_ct3, study, indexes)
number_of_covid_layers += len(indexes)

# SET CT-2

# Study 0939
study = get_study_name('0939')
indexes = list(range(28, 38, 1))
append_study(data_folder_ct2, study, indexes)
number_of_covid_layers += len(indexes)

# Study 0940
study = get_study_name('0940')
indexes = list(range(18, 29, 1))
append_study(data_folder_ct2, study, indexes)
number_of_covid_layers += len(indexes)

# Study 0941
study = get_study_name('0941')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct2, study, indexes)
number_of_covid_layers += len(indexes)

# Study 0942
study = get_study_name('0942')
indexes = list(range(20, 30, 1))
append_study(data_folder_ct2, study, indexes)
number_of_covid_layers += len(indexes)

# Study 0943
study = get_study_name('0943')
indexes = list(range(19, 30, 1))
append_study(data_folder_ct2, study, indexes)
number_of_covid_layers += len(indexes)

# Study 0944
study = get_study_name('0944')
indexes = list(range(14, 25, 1))
append_study(data_folder_ct2, study, indexes)
number_of_covid_layers += len(indexes)

# Study 0945
study = get_study_name('0945')
indexes = list(range(16, 23, 1))
append_study(data_folder_ct2, study, indexes)
number_of_covid_layers += len(indexes)


print("Covid set done")

# SUMMARY ##########################################################################################################
print("Normal layers: {0}".format(number_of_normal_layers))
print("Covid layers: {0}".format(number_of_covid_layers))

train_name = 'KMeansLungWindowRussia'


def dump_image_ensemble(name):
    global e
    dump(e, "imageEnsemble{0}.joblib".format(name))
    print("dump ensemble done")
    
    
def load_image_ensemble(name):
    global e
    e = load("imageEnsemble{0}.joblib".format(name))
    print("load ensemble done")


def subset_image_ensemble():
    global e
    normal_subset = e.lungs[0:150]
    covid_subset = e.lungs[600:]
    e.lungs = normal_subset + covid_subset
    print(len(e.lungs))


# # Odkomentować wybrane
dump_image_ensemble(train_name)
# load_image_ensemble(train_name)
# subset_image_ensemble()


print("Number of layers: {0}".format(len(e.lungs)))

# GLCM #############################################################################################################
e.GetMatrices()
e.GetProps()
glcmFts = e.props
dump(glcmFts, 'glcmFeatures{0}.joblib'.format(train_name))
print('glcm done')

# Haralick ##########################################################################################################
h = Haralick(e.lungs)
haralickFts = h.GetHaralickFtsAll()
# # # dump(np.hstack((haralickFts, glcmFts)),'glcmHaralickFeatures.joblib')
print('haralick done')

# Alexnet ##########################################################################################################

# alex = Alex(load('featureExtraction.joblib'))
# alexFts = alex.GetFeaturesFromList(e.lungs)
# alexFts = alex.ChangeDimAndStandardize(alexFts)
# alexFts = alex.DoPCA(alexFts, n=50)
# print('alex done')


def dump_alex_features(name):
    global alexFts
    dump(alexFts, 'alexFeatures_{}.joblib'.format(name))
    print('dump alex done')


# alexFts = load('alexFeatures_{}.joblib'.format(train_name))
# print("load alex done")

# Classifier ########################################################################################################
cc = ClassifierCombination()
cc.make_array2(haralickFts, glcmFts)
# cc.make_array1(alexFts)
cc.get_labels()


print("Cross evaluate cv 5")
tn, fp, fn, tp = cc.cross_evaluateLD(cv=5)
sen, spe, ppv, npv, acc, mcc = cc.get_measures(tp, tn, fp, fn)
print(sen, spe, ppv, npv, acc)

print("Cross evaluate cv 10")
tn, fp, fn, tp = cc.cross_evaluateLD(cv=10)
sen, spe, ppv, npv, acc, mcc = cc.get_measures(tp, tn, fp, fn)
print(sen, spe, ppv, npv, acc)

print("Cross evaluate cv 15")
tn, fp, fn, tp = cc.cross_evaluateLD(cv=15)
sen, spe, ppv, npv, acc, mcc = cc.get_measures(tp, tn, fp, fn)
print(sen, spe, ppv, npv, acc)
