import pickle
from joblib import dump, load
import sys,os
from pathlib import Path
sys.path.append(str(Path().resolve().parent))
from glcm import *
from alexnet import Alex
from sklearn import metrics



from glcm import *

# model = load('glcmModelFitFinal.joblib') 

# e = ImageEnsemble([r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\csTest"],gotFolders=True)
# e.MakeDicoms()
# e.GetLungs()
# e.GetMatrices()
# e.GetProps()

# y_test = model.predict(e.props)
y_pred = []
for i in range(11):
    y_pred.append('normal')
for i in range(9):
    y_pred.append('covid')
# # Model Accuracy: how often is the classifier correct?
# print("Accuracy:",metrics.accuracy_score( y_pred,y_test))
# # Model Precision: what percentage of positive tuples are labeled as such?
# print(np.array(y_pred))
# print(y_test)
# print("Precision:",metrics.precision_score(np.array(y_pred),y_test,pos_label='covid'))

# # Model Recall: what percentage of positive tuples are labelled as such?
# print("Recall:",metrics.recall_score(np.array(y_pred),y_test,pos_label='covid'))


data_folder = r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\cs"#w srodku 10 roznych ct po 10 dcm
test_folder = r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\csTest" #w srodku 1 dcm

start = time.time()
# dcms = []
# dcms.append(test_folder)

e = ImageEnsemble([r"C:\Users\Maya\studia\4rok\inz\repo\covidSeg\csTest"],gotFolders=True)
e.MakeDicoms()
e.GetLungs()

alex = Alex(load('featureExtraction.joblib'))
testft = alex.GetFeaturesFromList(e.lungs)
print("przed change dim")
print(len(testft))
print(len(testft[0]))
testft = alex.ChangeDimAndStandardize(testft,isTensor=True)
print("po change dim")
print(len(testft))
print(len(testft[0]))
newfts = load('csPrePCAFeatures.joblib')
print("zaladowane macierze")
print(len(newfts))
print(len(newfts[0]))
for f in testft:
    newfts.append(f)
print(len(newfts))
print(len(newfts[0]))
pcafts = alex.DoPCA(newfts)
print("po pca")
print(len(pcafts))
print(len(pcafts[0]))

labels = []
for i in range(50):
    labels.append('covid')
for i in range(50):
    labels.append('normal')


# print(len(pcafts))
model=load('alexnetModel.joblib')
model.fit(pcafts[0:100],labels)
y_test2 = model.predict(pcafts[100:120])
print(y_test2)
print("Execution time: ",time.time()-start)
print("Accuracy:",metrics.accuracy_score( y_pred,y_test2))
# Model Precision: what percentage of positive tuples are labeled as such?

print("Precision:",metrics.precision_score(np.array(y_pred),y_test2,pos_label='covid'))

# Model Recall: what percentage of positive tuples are labelled as such?
print("Recall:",metrics.recall_score(np.array(y_pred),y_test2,pos_label='covid'))