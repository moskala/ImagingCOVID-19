# Kivy imports
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
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
from ExaminationType import ExaminationType

# Paths
MODELS_FOLDER_PATH = str(Path().resolve().parent.parent / "models")
MODELS_XRAY_FOLDER_PATH = str(Path().resolve().parent.parent / "models"/"xray")

MODEL_ALEX_EXTRACT_NAME = "featureExtraction.joblib"
# MODEL_ALEX_EXTRACT = load(MODEL_ALEX_EXTRACT_PATH)
MODEL_GLCM_HARALICK_DATA_NAME = "glcmHaralickData.joblib"
MODEL_ALEX_DATA_NAME = "prePCAFeatures50.joblib"
# MODEL_ALEX_DATA = load(MODEL_ALEX_DATA_PATH)
# MODEL_ALEX_SVM = load(MODEL_ALEX_SVM_PATH)

class AutomaticResultPopup(Popup):
    scroll_view = ObjectProperty(None)

class AnalysisPopup(Popup):
    image_object = ObjectProperty(None)
    analysis = ObjectProperty(None)
    box_layout = ObjectProperty(None)
    current_model = ObjectProperty(None)
    current_features = None
    def __init__(self,analysis,image_object,current_model,examination_type,indexes = None):
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
        self.examination_type = examination_type

    def make_content_for_result_popup(self,text):
        bl = BoxLayout(orientation='vertical')
        scroll_view = ScrollView(do_scroll_x=True,do_scroll_y=True,size_hint_max_y=200)
        label = Label(size_hint_y=None,halign='justify',text_size=(self.width, None),text=text,padding=(20,20))
        label.bind(height=self.setter('texture_size[1]'))# - jak to sie robi?
        scroll_view.add_widget(label)
        bl.add_widget(scroll_view)
        #label = Label(text=text)
        return bl
    
    def add_result_to_analysis(self,isAlex,prediction,slic,layer_number,model):
        properties = self.image_object.get_info()
        if(isAlex):
            result = AlexnetResult(prediction,slic,properties["Height"],properties["Width"],properties["CT Window Type"],properties["Filename"],layer_number,self.examination_type,model)
        else:
            result = HaralickGlcmResult(prediction,slic,properties["Height"],properties["Width"],properties["CT Window Type"],properties["Filename"],layer_number,self.examination_type,model)
        self.analysis.add_to_list(result)
        #dict
        dict_key = properties["Filename"]+"_"+str(layer_number)
        if(dict_key in self.analysis.dictionary[self.analysis.current_analysis_index]):
            self.analysis.dictionary[self.analysis.current_analysis_index][dict_key].append(prediction)
        else:
            temp_list = [prediction]
            
            self.analysis.dictionary[self.analysis.current_analysis_index].update({dict_key: temp_list})
        print('Added following result to collection: ',result.get_object_properties_list())

    def analysis_classify_recent(self,unknown_argumentxd):
        if(self.examination_type is ExaminationType.XRAY):
            MODEL_GLCM_HARALICK_DATA_PATH = os.path.join(MODELS_XRAY_FOLDER_PATH,MODEL_GLCM_HARALICK_DATA_NAME)
            MODEL_ALEX_EXTRACT_PATH =  os.path.join(MODELS_XRAY_FOLDER_PATH,MODEL_ALEX_EXTRACT_NAME)
            MODEL_ALEX_DATA_PATH = os.path.join(MODELS_XRAY_FOLDER_PATH,MODEL_ALEX_DATA_NAME)
        else:
            MODEL_GLCM_HARALICK_DATA_PATH = os.path.join(MODELS_FOLDER_PATH,MODEL_GLCM_HARALICK_DATA_NAME)
            MODEL_ALEX_EXTRACT_PATH =  os.path.join(MODELS_FOLDER_PATH,MODEL_ALEX_EXTRACT_NAME)
            MODEL_ALEX_DATA_PATH = os.path.join(MODELS_FOLDER_PATH,MODEL_ALEX_DATA_NAME)
        if(self.current_model is not None):
            for index in self.indexes:
                self.image_object.get_specific_slice(index)
                if(self.current_features is 'GlcmHaralick'):
                    predict,_ = PredictGlcmHaralick(self.image_object.get_specific_slice(index),self.current_model,MODEL_GLCM_HARALICK_DATA_PATH,self.examination_type,isPretrained=False)

                else:
                    predict,_ = PredictAlex(self.image_object.get_specific_slice(index),MODEL_ALEX_EXTRACT_PATH,
                                        MODEL_ALEX_DATA_PATH,self.current_model,self.examination_type,isPretrained=False)
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
                text = self.analysis.add_summary_to_text_element()
            popup = AutomaticResultPopup(title='Result',size=(600,400),size_hint=(None, None))
            popup.scroll_view.text = text
            popup.info.text = '\nAutomatic analysis finished!\n Go to \'Reports\' to generate a report file'
            popup.open()
            self.dismiss()
    def analysis_classify_train(self):
        # first we train for the first index
        if(self.examination_type is ExaminationType.XRAY):
            MODEL_GLCM_HARALICK_DATA_PATH = os.path.join(MODELS_XRAY_FOLDER_PATH,MODEL_GLCM_HARALICK_DATA_NAME)
            MODEL_ALEX_EXTRACT_PATH =  os.path.join(MODELS_XRAY_FOLDER_PATH,MODEL_ALEX_EXTRACT_NAME)
            MODEL_ALEX_DATA_PATH = os.path.join(MODELS_XRAY_FOLDER_PATH,MODEL_ALEX_DATA_NAME)
        else:
            MODEL_GLCM_HARALICK_DATA_PATH = os.path.join(MODELS_FOLDER_PATH,MODEL_GLCM_HARALICK_DATA_NAME)
            MODEL_ALEX_EXTRACT_PATH =  os.path.join(MODELS_FOLDER_PATH,MODEL_ALEX_EXTRACT_NAME)
            MODEL_ALEX_DATA_PATH = os.path.join(MODELS_FOLDER_PATH,MODEL_ALEX_DATA_NAME)
        first_index = self.indexes[0]
        self.image_object.get_specific_slice(first_index)
        if(self.trainGlcmHaralick.state is'down'):
            self.current_features = 'GlcmHaralick'
            if(self.trainRandomForest.state is 'down'):
                if(self.trainAuto.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model().modelRandomForest,MODEL_GLCM_HARALICK_DATA_PATH,self.examination_type,isPretrained=False)
                elif(self.trainSqrt.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model(max_features='sqrt').modelRandomForest,MODEL_GLCM_HARALICK_DATA_PATH,self.examination_type,isPretrained=False)
                else:
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model(max_features='log2').modelRandomForest,MODEL_GLCM_HARALICK_DATA_PATH,self.examination_type,isPretrained=False)
                temp_model = Model().modelRandomForest
            else:
                if(self.trainLbfgs.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model().modelLogisticRegression,MODEL_GLCM_HARALICK_DATA_PATH,self.examination_type,isPretrained=False)
                elif(self.trainLiblinear.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model(solver='liblinear').modelLogisticRegression,MODEL_GLCM_HARALICK_DATA_PATH,self.examination_type,isPretrained=False)
                else:
                    predict,self.current_model = PredictGlcmHaralick(self.image_object.get_specific_slice(first_index),Model(solver='saga').modelLogisticRegression,MODEL_GLCM_HARALICK_DATA_PATH,self.examination_type,isPretrained=False)
                temp_model = Model().modelLogisticRegression
        else:
            self.current_features = 'Alexnet'
            if(self.trainRandomForest.state is 'down'):
                if(self.trainAuto.state is 'down'):
                   predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model().modelRandomForest,self.examination_type,isPretrained=False)
                elif(self.trainSqrt.state is 'down'):
                    predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(max_features='sqrt').modelRandomForest,self.examination_type,isPretrained=False)
                else:
                    predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(max_features='log2').modelRandomForest,self.examination_type,isPretrained=False)
                temp_model = Model().modelRandomForest
            else:
                if(self.trainLbfgs.state is 'down'):
                    predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model().modelLogisticRegression,self.examination_type,isPretrained=False)
                elif(self.trainLiblinear.state is 'down'):
                    predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(solver='liblinear').modelLogisticRegression,self.examination_type,isPretrained=False)
                else:
                    predict,self.current_model = PredictAlex(self.image_object.get_specific_slice(first_index),MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(solver='saga').modelLogisticRegression,self.examination_type,isPretrained=False)
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
            text = self.analysis.add_summary_to_text_element()
        popup = AutomaticResultPopup(title='Result',size=(600,400),size_hint=(None, None))
        popup.scroll_view.text = text
        popup.info.text = '\nAutomatic analysis finished!\n Go to \'Reports\' to generate a report file'
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


        if(self.examination_type is ExaminationType.XRAY):
            classifier_path = os.path.join(MODELS_XRAY_FOLDER_PATH,filename)
            MODEL_GLCM_HARALICK_DATA_PATH = os.path.join(MODELS_XRAY_FOLDER_PATH,MODEL_GLCM_HARALICK_DATA_NAME)
            MODEL_ALEX_EXTRACT_PATH =  os.path.join(MODELS_XRAY_FOLDER_PATH,MODEL_ALEX_EXTRACT_NAME)
            MODEL_ALEX_DATA_PATH = os.path.join(MODELS_XRAY_FOLDER_PATH,MODEL_ALEX_DATA_NAME)
        else:
            classifier_path = os.path.join(MODELS_FOLDER_PATH,filename)
            MODEL_GLCM_HARALICK_DATA_PATH = os.path.join(MODELS_FOLDER_PATH,MODEL_GLCM_HARALICK_DATA_NAME)
            MODEL_ALEX_EXTRACT_PATH =  os.path.join(MODELS_FOLDER_PATH,MODEL_ALEX_EXTRACT_NAME)
            MODEL_ALEX_DATA_PATH = os.path.join(MODELS_FOLDER_PATH,MODEL_ALEX_DATA_NAME)

        for index in self.indexes:
            if(self.preGlcmHaralick.state is'down'):
                self.image_object.get_specific_slice(index)
                predict,_ = PredictGlcmHaralick(self.image_object.get_specific_slice(index),classifier_path,MODEL_GLCM_HARALICK_DATA_PATH,self.examination_type)

                self.current_features_for_automatic = 'GlcmHaralick'
            else:
                predict,_ = PredictAlex(self.image_object.get_specific_slice(index),MODEL_ALEX_EXTRACT_PATH,
                                        MODEL_ALEX_DATA_PATH,
                                        classifier_path,self.examination_type)
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
            text = self.analysis.add_summary_to_text_element()
        popup = AutomaticResultPopup(title='Result',size=(600,400),size_hint=(None, None))
        popup.scroll_view.text = text
        popup.info.text = '\nAutomatic analysis finished!\n Go to \'Reports\' to generate a report file'
        popup.open()
        self.dismiss()
