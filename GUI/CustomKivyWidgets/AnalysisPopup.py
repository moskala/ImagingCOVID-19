# Kivy imports
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

# Custom kivy widgets imports


# Python imports
from pathlib import Path
import sys
sys.path.append(str(Path().resolve().parent.parent / "Methods"))

# Implemented methods imports
from PredictAlexnet import *
from PredictGlcmHaralick import *
from ChooseSlices import *
from Grayscale import *
from Analysis.Analysis import *
from Analysis.Result import *

# Paths
MODELS_FOLDER_PATH = str(Path().resolve().parent.parent / "models")
MODEL_GLCM_PATH = str(Path().resolve().parent.parent / "models" / "glcmModelFitFinal.joblib")
MODEL_ALEX_EXTRACT_PATH = str(Path().resolve().parent.parent / "models" / "featureExtraction.joblib")
# MODEL_ALEX_EXTRACT = load(MODEL_ALEX_EXTRACT_PATH)
MODEL_GLCM_HARALICK_DATA_PATH = str(Path().resolve().parent.parent / "models" / "glcmHaralickData.joblib")
MODEL_ALEX_DATA_PATH = str(Path().resolve().parent.parent / "models" / "csPrePCAFeatures50.joblib")
# MODEL_ALEX_DATA = load(MODEL_ALEX_DATA_PATH)
# MODEL_ALEX_SVM = load(MODEL_ALEX_SVM_PATH)
MODEL_HARALICK_PATH = str(Path().resolve().parent.parent / "models" / "haralickSVM.joblib")


class AnalysisPopup(Popup):
    image_object = ObjectProperty(None)
    analysis = ObjectProperty(None)
    box_layout = ObjectProperty(None)
    current_model = ObjectProperty(None)
    current_features = None
    def __init__(self,analysis,image_object,current_model,indexes = None):
        super().__init__()
        self.image_object = image_object
        self.analysis = analysis
        self.current_model = current_model
        if(indexes is None):
            self.indexes = []
            self.indexes.append(image_object.current_slice_number)
            print(image_object.current_slice_number)
        else:
            self.indexes = indexes

    def add_result_to_analysis(self,isAlex,prediction,slic,layer_number,model):
        properties = self.image_object.get_info()
        if(isAlex):
            result = AlexnetResult(prediction,slic,properties["Height"],properties["Width"],properties["CT Window Type"],properties["Filename"],layer_number,model)
        else:
            result = HaralickGlcmResult(prediction,slic,properties["Height"],properties["Width"],properties["CT Window Type"],properties["Filename"],layer_number,model)
        self.analysis.add_to_list(result)
        #dict
        if(properties["Filename"] in self.analysis.dictionary[self.analysis.current_analysis_index]):
            self.analysis.dictionary[self.analysis.current_analysis_index][properties["Filename"]].append(prediction)
        else:
            temp_list = [prediction]
            print(properties["Filename"],type(properties["Filename"]))
            self.analysis.dictionary[self.analysis.current_analysis_index].update({properties["Filename"]: temp_list})
        print('Added following result to collection: ',result.get_object_properties_list())

    def analysis_classify_recent(self,unknown_argumentxd):
        if(self.current_model is not None):
            for index in self.indexes:
                self.image_object.get_specific_slice(index)
                if(self.current_features is 'GlcmHaralick'):
                    predict,_ = PredictGlcmHaralick(self.image_object.get_specific_slice(index),self.current_model,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)

                else:
                    predict,_ = PredictAlex(self.image_object.get_specific_slice(index),MODEL_ALEX_EXTRACT_PATH,
                                        MODEL_ALEX_DATA_PATH,self.current_model,isPretrained=False)
                if(predict[0]=='normal'):
                    prediction = 'Normal'
                else:
                    prediction = 'COVID-19'

                if(self.trainAlex.state is 'down'):
                    self.add_result_to_analysis(True,prediction,self.image_object.get_specific_slice(index),index,self.current_model)
                else:
                    self.add_result_to_analysis(False,prediction,self.image_object.get_specific_slice(index),index,self.current_model)
            if(len(self.indexes)<=1):
                text = prediction
            else:
                text = 'Automatic analysis finished!\n Go to \'Reports\' to generate a report file'
            popup = Popup(title='Result',content=Label(text=text),size=(400, 400),size_hint=(None, None))
            popup.open()
            self.dismiss()
    def analysis_classify_train(self):
        # first we train for the first index
        first_index = self.indexes[0]
        self.image_object.get_specific_slice(first_index)
        if(self.trainGlcmHaralick.state is'down'):
            self.current_features = 'GlcmHaralick'
            if(self.trainRandomForest.state is 'down'):
                if(self.trainAuto.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model().modelRandomForest,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
                elif(self.trainSqrt.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model(max_features='sqrt').modelRandomForest,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
                else:
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model(max_features='log2').modelRandomForest,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
                temp_model = Model().modelRandomForest
            else:
                if(self.trainLbfgs.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model().modelLogisticRegression,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
                elif(self.trainLiblinear.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model(solver='liblinear').modelLogisticRegression,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
                else:
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model(solver='saga').modelLogisticRegression,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
                temp_model = Model().modelLogisticRegression
        else:
            self.current_features = 'Alexnet'
            if(self.trainRandomForest.state is 'down'):
                if(self.trainAuto.state is 'down'):
                   predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model().modelRandomForest,isPretrained=False)
                elif(self.trainSqrt.state is 'down'):
                    predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(max_features='sqrt').modelRandomForest,isPretrained=False)
                else:
                    predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(max_features='log2').modelRandomForest,isPretrained=False)
                temp_model = Model().modelRandomForest
            else:
                if(self.trainLbfgs.state is 'down'):
                    predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model().modelLogisticRegression,isPretrained=False)
                elif(self.trainLiblinear.state is 'down'):
                    predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(solver='liblinear').modelLogisticRegression,isPretrained=False)
                else:
                    predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(solver='saga').modelLogisticRegression,isPretrained=False)
                temp_model = Model().modelLogisticRegression

        if(predict[0]=='normal'):
            prediction = 'Normal'
        else:
            prediction = 'COVID-19'
        if(self.trainAlex.state is 'down'):
            self.add_result_to_analysis(True,prediction,self.image_object.get_specific_slice(first_index),first_index,temp_model)
        else:
            self.add_result_to_analysis(False,prediction,self.image_object.get_specific_slice(first_index),first_index,temp_model)


        # for rest of indexes we do analysis classify recent
        if(len(self.indexes)>1):
            self.indexes.pop(0)
            self.analysis_classify_recent(0)

    # print(self.current_model)
        print('len indexes: ',len(self.indexes))
        if(len(self.indexes)<=1):
            text = prediction
        else:
            text = 'Automatic analysis finished!\n Go to \'Reports\' to generate a report file'
        popup = Popup(title='Result',content=Label(text=text),size=(400, 400),size_hint=(None, None))
        popup.open()


        self.dismiss()

    def analysis_classify_pretrained(self):
        filename = ""
        if(self.preGlcmHaralick.state is'down'):
            filename+='glcmHaralick'
            if(self.preSvm.state is 'down'):
                filename+='Svm'
                if(self.preLinear.state is 'down'):
                    filename+='Linear.joblib'
                else:
                    filename+='Rbf.joblib'
            else:
                filename+='LinearDiscriminant'
                if(self.preSvd.state is 'down'):
                    filename+='Svd.joblib'
                else:
                    filename+='Lsqr.joblib'
        else:
            filename+='alexnet'
            if(self.preSvm.state is 'down'):
                filename+='Svm'
                if(self.preLinear.state is 'down'):
                    filename+='Linear.joblib'
                else:
                    filename+='Rbf.joblib'
            else:
                filename+='LinearDiscriminant'
                if(self.preSvd.state is 'down'):
                    filename+='Svd.joblib'
                else:
                    filename+='Lsqr.joblib'



        classifier_path = os.path.join(MODELS_FOLDER_PATH,filename)

        for index in self.indexes:
            if(self.preGlcmHaralick.state is'down'):
                self.image_object.get_specific_slice(index)
                predict,_ = PredictGlcmHaralick(self.image_object.get_specific_slice(index),classifier_path,MODEL_GLCM_HARALICK_DATA_PATH)

                self.current_features_for_automatic = 'GlcmHaralick'
            else:
                predict,_ = PredictAlex(self.image_object.get_specific_slice(index),MODEL_ALEX_EXTRACT_PATH,
                                        MODEL_ALEX_DATA_PATH,
                                        classifier_path)
                self.current_features_for_automatic = 'Alexnet'
            if(predict[0]=='normal'):
                prediction = 'Normal'
            else:
                prediction = 'COVID-19'

            if(self.preAlex.state is 'down'):
                self.add_result_to_analysis(True,prediction,self.image_object.get_specific_slice(index),index,load(classifier_path))
            else:
                self.add_result_to_analysis(False,prediction,self.image_object.get_specific_slice(index),index,load(classifier_path))
        if(len(self.indexes)<=1):
            text = prediction
        else:
            text = 'Automatic analysis finished!\n Go to \'Reports\' to generate a report file'
        popup = Popup(title='Result',content=Label(text=text),size=(400, 400),size_hint=(None, None))
        popup.open()
        self.dismiss()
