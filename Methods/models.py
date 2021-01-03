from joblib import dump,load


model = load('glcmHaralickSvmRbf.joblib')
print(model.kernel)