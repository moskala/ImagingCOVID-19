import matplotlib
# matplotlib.use('Agg', force=True)  # comment this line to see effect
import matplotlib.pyplot as plt
from kivy.app import App
from  kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse,Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image as UixImage
from kivy.uix.slider import Slider
import pydicom
from pathlib import Path
import sys
from PIL import Image
import csv
import os,time
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
# matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from jinja2 import Environment, BaseLoader
import pdfkit
from Pdf import *
sys.path.append(str(Path().resolve().parent / "Methods"))

from LungSegmentation.LungSegmentation_MethodA_dicom import SegmentationA
from LungSegmentation.LungSegmentation_MethodB_dicom import SegmentationB
import LungSegmentation.LungSegmentation_MethodKMeans_AllTypes as segmentation
import Show_matplotlib_all as show
from ImageClass import *
from net.testNet import Net
from PredictGLCM import *
from PredictAlexnet import *
from PredictHaralick import *
from PredictGlcmHaralick import *
from Grayscale import * 
from joblib import load
import imageio
from datetime import date
from ChooseSlices import *


sys.path.append(str(Path().resolve().parent / "Methods" / "Analysis"))
from Analysis import * 
from Result import *

MY_FOLDER = Path()
MODELS_FOLDER_PATH = str(Path().resolve().parent.parent/ "models")
MODEL_PATH = str(Path().resolve().parent.parent / "models" / "best_checkpoint.pth")
MODEL_ALEX_EXTRACT_PATH = str(Path().resolve().parent.parent / "models" / "featureExtraction.joblib")
# MODEL_ALEX_EXTRACT = load(MODEL_ALEX_EXTRACT_PATH)
MODEL_GLCM_HARALICK_DATA_PATH = str(Path().resolve().parent.parent / "models" / "glcmHaralickData.joblib")
MODEL_ALEX_DATA_PATH = str(Path().resolve().parent.parent / "models" / "csPrePCAFeatures50.joblib")
# MODEL_ALEX_DATA = load(MODEL_ALEX_DATA_PATH)
# MODEL_ALEX_SVM = load(MODEL_ALEX_SVM_PATH)
GUI_FOLDER = str(Path().resolve())
START_IMAGE = "sample_image.jpg"


class MyPaintWidget(Widget):
    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 1, 0)
            d = 30.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))

class MyFigure(FigureCanvasKivyAgg):
    """This class is used to display an image in GUI"""
    def __init__(self, val=0, image_data=None, **kwargs):
        """constructor"""
        if image_data is None:
            image_data = show.get_plot_data_jpg_png('sample_image.jpg')
        plt.axis('off')
        plt.imshow(image_data, cmap='gray')
        super(MyFigure, self).__init__(plt.gcf(), **kwargs)
        self.curPlt = plt.gcf()
        self.image_data = image_data
        self.val = val


class MyPaintFigure(MyFigure):
    draw_points=None
    def __init__(self,image_data,**kwargs):
        super().__init__(image_data=image_data)
        self.draw_points=[]
    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 1, 0)
            touch.apply_transform_2d(self.to_widget)
            d = 5.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            print((touch.x-self.pos[0],touch.y-self.pos[1]))
            print(self.draw_points)
    def get_points(self):
        return self.draw_points

class MyImage(UixImage):
    draw_points=None
    img_width = None
    img_height=None
    def __init__(self,image_data,**kwargs):
        image = Image.fromarray(convert_array_to_grayscale(image_data))
        image.save('test.jpg')
        super().__init__(source='test.jpg')
        self.draw_points=[]
        self.img_width = image.width
        self.img_height = image.height
        #os.remove('test.jpg')
    def on_touch_down(self, touch):
        new_img_width =self.size[1]*self.img_width/ self.img_height
        margin = (self.size[0]-new_img_width)/2+self.pos[0]
        print('margin ',margin)
        with self.canvas:
            Color(1, 1, 0)
            print('self ',self)
            print('self size ',self.size)
            print('self pos ',self.pos)
            print('touch ',touch.x-margin,touch.y-self.pos[1])
            d = 5.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            if(touch.y-self.pos[1]<self.size[1]):
                self.draw_points.append((int(touch.x-margin),int(touch.y-self.pos[1])))
    def get_points(self):
        return self.draw_points


class ResultPopup(Popup):
    analysis = ObjectProperty(None)
    content = ObjectProperty(None)
    comments = ObjectProperty(None)
    def __init__(self,analysis):
        super().__init__()
        self.analysis = analysis
    def calculate_results(self):
        how_many_results = [0,0,0] #0-normal,1-covid,2-undefined
        for key in self.analysis.dictionary:
            how_many_results_temp = [0,0]
            for result in self.analysis.dictionary[key]:
                if(result=='COVID-19'):
                    how_many_results_temp[1]+=1
                elif(result=='Normal'):
                    how_many_results_temp[0]+=1
            if(how_many_results_temp[0]>0 and how_many_results_temp[1]==0):
                how_many_results[0]+=1
            elif(how_many_results_temp[1]>0 and how_many_results_temp[0]==0):
                how_many_results[1]+=1
            else:
                how_many_results[2]+=1
        return how_many_results
    def get_result_array(self,result,withHeaders = False):
        res = result.get_object_properties_list()
        res.pop(1)
        res.append(result.get_method_name())
        res.insert(0,self.analysis.result_list.index(result)+1)
        if(withHeaders):
            headers = result.get_object_properties_headers()
            nres = np.asarray(res)
            nheaders = np.asarray(headers)
            # array with one result
            nres = np.column_stack((nheaders,nres))
            return nres
        else:
            return res

    def generate_report_pdf(self,folder,filename):
        print('comments ',self.comments)
        outputFile = folder+'/'+filename
        if(self.analysis is None):
                print("No analisys has been made yet")
                self._popup.dismiss()
                return
        else:
            dateStr = 'Report generated on '+date.today().strftime("%d/%m/%Y")+'\n'
            how_many_slices_analized = len(self.analysis.dictionary.keys())
            how_many_slices_total = self.analysis.slices_number
            how_many_results = self.calculate_results()
            sheaders = np.asarray(self.analysis.get_analysis_summary_headers())
            snumbers = np.asarray(self.analysis.get_analysis_summary_numbers(how_many_slices_total,how_many_slices_analized,how_many_results))
            snumbers = np.column_stack((sheaders,snumbers))
             #pdf
            pdf = PDF()
            pdf.add_page()
            # width and height for A4
            pdf_w=210
            pdf_h=297
            font_size = 11
            epw = pdf.w - 2*pdf.l_margin
            # title
            pdf.ln(font_size)
            pdf.set_font_characteristics(font_size=font_size,isBold=True)
            pdf.cell(epw, 0.0, dateStr, align='C')
            pdf.ln(3*font_size)
            # set font
            pdf.set_font_characteristics(font_size=font_size)
            pdf.cell(epw, 0.0, 'Comments', align='C')
            pdf.ln(font_size)
            pdf.cell(epw, 0.0, self.comments, align='L')
            pdf.ln(font_size)
            pdf.cell(epw, 0.0, 'Analysis details', align='C')
            pdf.ln(font_size)
            for result in self.analysis.result_list:
                if(self.analysis.result_list.index(result)==0):
                    # array with one result
                    nres = np.transpose(self.get_result_array(result,withHeaders=True))
                    for row in nres:
                        for col in row:
                            pdf.cell(epw/7, font_size, str(col), border=1)
                        pdf.ln(font_size)
                else:
                    nres = np.transpose(self.get_result_array(result))
                    for col in nres:
                        pdf.cell(epw/7, font_size, str(col), border=1)
                    pdf.ln(font_size)
            pdf.ln(3*font_size)
            pdf.cell(epw, 0.0, 'Analized images', align='C')  
            pdf.ln(font_size)
            for result in self.analysis.result_list:
                res = result.get_object_properties_list()
                lungs = res[1]
                lung_image = convert_array_to_grayscale(lungs)
                im = Image.fromarray(lung_image)
                temp_image = folder+'/test.jpg'
                imageio.imwrite(temp_image, lung_image)
                pdf.add_image_basic(temp_image,res[2]/5,res[3]/5,pdf_w)
                os.remove(temp_image)
                pdf.ln(font_size)

            pdf.ln(3*font_size)
            pdf.cell(epw, 0.0, 'Summary', align='C') 
            pdf.ln(font_size)
            for row in snumbers:
                for col in row:
                    pdf.cell(epw/2, font_size, str(col), border=1)
                pdf.ln(font_size)  
            #saving
            pdf.output(outputFile,'F')
            self._popup.dismiss()

    def generate_report_csv(self,folder,filename):
        print('comments ',self.comments)
        outputFile = folder+'/'+filename
        if(self.analysis is None):
                print("No analisys has been made yet")
                self._popup.dismiss()
                return
        else:
            dateStr = 'Report generated on '+date.today().strftime("%d/%m/%Y")+'\n'
            how_many_slices_analized = len(self.analysis.dictionary.keys())
            how_many_slices_total = self.analysis.slices_number
            how_many_results = self.calculate_results()
            sheaders = np.asarray(self.analysis.get_analysis_summary_headers())
            snumbers = np.asarray(self.analysis.get_analysis_summary_numbers(how_many_slices_total,how_many_slices_analized,how_many_results))
            snumbers = np.column_stack((sheaders,snumbers))

            with open(outputFile, mode='w') as analysis_file:
                # add title
                analysis_file.write(dateStr)
                analysis_file.write('\n')
                analysis_file.write('Comments\n')
                analysis_file.write(self.comments)
                analysis_file.write('\n')
                analysis_file.write('\n')
                analysis_file.write('Analysis details\n')
                analysis_file.write('\n')
                # add all results
                for result in self.analysis.result_list:
                    # array with one result
                    nres = self.get_result_array(result,withHeaders=True)
                    np.savetxt(analysis_file,nres,delimiter=',',fmt='%s')
                    analysis_file.write("\n")
                # summary
                analysis_file.write('\n')
                analysis_file.write('Summary\n')
                analysis_file.write('\n')
                np.savetxt(analysis_file,snumbers,delimiter=',',fmt='%s')
                analysis_file.write("\n")
                self._popup.dismiss()
            
    def show_save_csv(self,comments):
        """This function runs save dialog"""
        self.comments=comments
        content = SaveDialog(save=self.generate_report_csv,  cancel=self.my_dismiss)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save_pdf(self,comments):
        """This function runs save dialog"""
        self.comments=comments
        content = SaveDialog(save=self.generate_report_pdf,  cancel=self.my_dismiss)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def my_dismiss(self):
        self._popup.dismiss()

class LoadDialog(FloatLayout):
    """This class is used to run the load dialog"""
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    """This class is used to run the save dialog"""
    save = ObjectProperty(None)
    img = ObjectProperty(None)
    cancel = ObjectProperty(None)

class DrawDialog(Popup):
    content = ObjectProperty(None)
        
class AnalysisDialog(Popup):
    image_object = ObjectProperty(None)
    analysis = ObjectProperty(None)
    box_layout = ObjectProperty(None)
    current_model = None
    current_features = None
    def __init__(self,analysis,image_object,current_model):
        super().__init__()
        self.image_object = image_object
        self.analysis = analysis
        self.current_model = current_model
    def add_result_to_analysis(self,isAlex,prediction):
        properties = self.image_object.get_info()
        if(isAlex):
            result = AlexnetResult(prediction,self.image_object.get_current_slice(),properties["Height"],properties["Width"],properties["CT Window Type"],properties["Filename"])
        else:
            result = HaralickGlcmResult(prediction,self.image_object.get_current_slice(),properties["Height"],properties["Width"],properties["CT Window Type"],properties["Filename"])
        self.analysis.add_to_list(result)
        #dict
        if(properties["Filename"] in self.analysis.dictionary):
            self.analysis.dictionary[properties["Filename"]].append(prediction)
        else:
            temp_list = [prediction]
            print(properties["Filename"],type(properties["Filename"]))
            self.analysis.dictionary.update({properties["Filename"]: temp_list})
        print('Added following result to collection: ',result.get_object_properties_list())

    def analysis_classify_recent(self,unknown_argumentxd):
        if(self.current_model is not None):
            if(self.current_features is 'GlcmHaralick'):
                predict,_ = PredictGlcmHaralick(self.image_object,self.current_model,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
            else:
                predict,_ = PredictAlex(self.image_object,MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,self.current_model,isPretrained=False)
            if(predict[0]=='normal'):
                prediction = 'Normal'
            else:
                prediction = 'COVID-19'  

            if(self.trainAlex.state is 'down'):
                self.add_result_to_analysis(True,prediction)
            else:
                self.add_result_to_analysis(False,prediction)
            popup = Popup(title='Result',content=Label(text=prediction),size=(400, 400),size_hint=(None, None))
            popup.open()
            self.dismiss()
    def analysis_classify_train(self):
        
        if(self.trainGlcmHaralick.state is'down'):
            self.current_features = 'GlcmHaralick'
            if(self.trainRandomForest.state is 'down'):
                if(self.trainAuto.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object,Model().modelRandomForest,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
                elif(self.trainSqrt.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object,Model(max_features='sqrt').modelRandomForest,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
                else:
                    predict,self.current_model = PredictGlcmHaralick(self.image_object,Model(max_features='log2').modelRandomForest,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
            else:
                if(self.trainLbfgs.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object,Model().modelLogisticRegression,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
                elif(self.trainLiblinear.state is 'down'):
                    predict,self.current_model = PredictGlcmHaralick(self.image_object,Model(solver='liblinear').modelLogisticRegression,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
                else:
                    predict,self.current_model = PredictGlcmHaralick(self.image_object,Model(solver='saga').modelLogisticRegression,MODEL_GLCM_HARALICK_DATA_PATH,isPretrained=False)
        else:
            self.current_features = 'Alexnet'
            if(self.trainRandomForest.state is 'down'):
                if(self.trainAuto.state is 'down'):
                   predict,self.current_model = PredictAlex(self.image_object,MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model().modelRandomForest,isPretrained=False)
                elif(self.trainSqrt.state is 'down'):
                    predict,self.current_model = PredictAlex(self.image_object,MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(max_features='sqrt').modelRandomForest,isPretrained=False)
                else:
                    predict,self.current_model = PredictAlex(self.image_object,MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(max_features='log2').modelRandomForest,isPretrained=False)
                
            else:
                if(self.trainLbfgs.state is 'down'):
                    predict,self.current_model = PredictAlex(self.image_object,MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model().modelLogisticRegression,isPretrained=False)
                elif(self.trainLiblinear.state is 'down'):
                    predict,self.current_model = PredictAlex(self.image_object,MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(solver='liblinear').modelLogisticRegression,isPretrained=False)
                else:
                    predict,self.current_model = PredictAlex(self.image_object,MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,Model(solver='saga').modelLogisticRegression,isPretrained=False)
                
        
        if(predict[0]=='normal'):
            prediction = 'Normal'
        else:
            prediction = 'COVID-19'  

        if(self.trainAlex.state is 'down'):
            self.add_result_to_analysis(True,prediction)
        else:
            self.add_result_to_analysis(False,prediction)
        print(self.current_model)
        popup = Popup(title='Result',content=Label(text=prediction),size=(400, 400),size_hint=(None, None))
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

        if(self.preGlcmHaralick.state is'down'):
            predict,_ = PredictGlcmHaralick(self.image_object,classifier_path,MODEL_GLCM_HARALICK_DATA_PATH)
           
        else:
            predict,_ = PredictAlex(self.image_object,MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,
                                     classifier_path)
        if(predict[0]=='normal'):
            prediction = 'Normal'
        else:
            prediction = 'COVID-19'  
        
        if(self.preAlex.state is 'down'):
            self.add_result_to_analysis(True,prediction)
        else:
            self.add_result_to_analysis(False,prediction)
        popup = Popup(title='Result',content=Label(text=prediction),size=(400, 400),size_hint=(None, None))
        popup.open()
        self.dismiss()

class CustomDropDown(DropDown):
    pass

class RootWidget(FloatLayout):
    """This class contains the root element for gui and all the necessary methods"""
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    image = ObjectProperty(None)
    # slider_val = ObjectProperty(None)
    result_grid = ObjectProperty(None)

    plot = None
    result = None

    image_object = JpgImage(GUI_FOLDER, START_IMAGE)

    _popup = None
    draw = None
    analysis = None
    current_model = None
    analysis_popup = None

    def analize_drawn(self):
        print(self.draw.draw_points)
    def draw_lesions(self):
        """
        Function creates draw lesions popup
        :return: None
        """
        print('draw lesions')
        try:
            popup = Factory.DrawDialog()
            self.draw = MyImage(image_data=self.plot.image_data)
            popup.draw_panel.add_widget(self.draw)
            popup.open()
        except Exception as error:
            print(error)

    def automatic_layer_choice(self):
        print(ChooseSlices(self.image_object))
        pass

    def slider_changed_value(self, value):
        """This function changes the displayed image when the slider is moved"""
        slice_number = int(value)
        if self.plot is not None and self.image_object is not None:
            self.left_panel.remove_widget(self.plot)
            self.plot = MyFigure(image_data=self.image_object.get_next_slice(slice_number))
            self.left_panel.add_widget(self.plot)
            self.slices_info.text = "Slice: {0}/{1}".format(self.image_object.current_slice_number+1,
                                                            self.image_object.total_slice_number)

    def load_next_slice(self, value):
        """This function changes the displayed image when the buttons 'Next' and 'Prev" are pressed"""
        shift = int(value)
        if self.plot is not None and self.image_object is not None:
            slice_number = self.image_object.current_slice_number + shift
            self.left_panel.remove_widget(self.plot)
            self.plot = MyFigure(image_data=self.image_object.get_next_slice(slice_number))
            self.left_panel.add_widget(self.plot)
            self.slices_info.text = "Slice: {0}/{1}".format(self.image_object.current_slice_number+1,
                                                            self.image_object.total_slice_number)
            self.slider.value = self.image_object.current_slice_number


    def dismiss_popup(self):
        """This function closes popup windows"""
        self._popup.dismiss()

    def neural_network(self):
        """This function runs the neural network process for the displayed image"""
        if self.image_object.file_type == ImageType.JPG or self.image_object.file_type == ImageType.PNG:
            self.net_label.text = Net.testImage(self.image_object.get_file_path(), MODEL_PATH)
        else:
            self.net_label.text = "Network accepts only jpg or png files!"

    # def glcm(self):
    #     """Classification using GLCM method."""
    #     try:
    #         prediction = PredictGLCM(self.image_object.src_folder,self.image_object.src_filename, MODEL_GLCM_PATH)
    #         print(prediction)
    #         if prediction[0] == 'normal':
    #             self.net_label.text = "Normal"
    #         else:
    #             self.net_label.text = "COVID-19"
    #     except Exception as error:
    #         print(error)
    #     self.add_result_to_analysis(False)
    
    # def alexnet(self):
    #     """Classification using Alexnet method."""
    #     try:
    #         prediction = PredictAlex(self.image_object.src_folder,
    #                                  self.image_object.src_filename,
    #                                  MODEL_ALEX_EXTRACT_PATH,
    #                                  MODEL_ALEX_DATA_PATH,
    #                                  MODEL_ALEX_SVM_PATH)
    #         print(prediction)
    #         if prediction[0] == 'normal':
    #             self.net_label.text = "Normal"
    #         else:
    #             self.net_label.text = "COVID-19"
    #     except Exception as error:
    #         print(error)
    #     self.add_result_to_analysis(True)

    # def haralick(self):
    #     prediction = PredictHaralick(self.image_object.src_folder,self.image_object.src_filename, MODEL_HARALICK_PATH)
    #     print(prediction)
    #     if(prediction[0]=='normal'):
    #         self.net_label.text = "Normal"
    #     else:
    #         self.net_label.text = "COVID-19"
    #     self.add_result_to_analysis(False)

    def lung_segment_binary(self):
        """This function runs binary lung segmentation"""
        try:
            if self.image_object.file_type != ImageType.DCM:
                print("This method is only for dicom files for now.")
                return
            image_folder = self.image_object.src_folder

            ct_scan = SegmentationB.read_ct_scan(image_folder)
            segmented_ct_scan = SegmentationB.segment_lung_from_ct_scan(ct_scan, self.image_object.current_slice_number)

            plt.imshow(segmented_ct_scan, cmap='gray')
            plt.axis('off')
            plt.show()
        except Exception as ex:
            print(ex)

    def lung_segment_watershed(self):
        """This function runs watershed segmentation"""
        try:
            if self.image_object.file_type != ImageType.DCM:
                print("This method is only for dicom files for now.")
                return

            image_folder = self.image_object.src_folder
            slices = SegmentationA.load_scan(image_folder)
            arr = SegmentationA.get_pixels_hu(slices)
            test_segmented, test_lungfilter, test_outline, test_watershed, test_sobel_gradient, test_marker_internal, \
                test_marker_external, test_marker_watershed = SegmentationA.seperate_lungs(arr[self.image_object.current_slice_number])

            plt.imshow(test_segmented, cmap='gray')
            plt.axis('off')
            plt.show()
        except Exception as ex:
            print(ex)

    def add_result_to_analysis(self,isAlex):
        properties = self.image_object.get_info()
        if(isAlex):
            result = AlexnetResult(self.net_label.text,self.image_object.get_current_slice(),properties["Height"],properties["Width"],properties["CT Window Type"],properties["Filename"])
        else:
            result = HaralickGlcmResult(self.net_label.text,self.image_object.get_current_slice(),properties["Height"],properties["Width"],properties["CT Window Type"],properties["Filename"])
        self.analysis.add_to_list(result)
        #dict
        if(properties["Filename"] in self.analysis.dictionary):
            self.analysis.dictionary[properties["Filename"]].append(self.net_label.text)
        else:
            temp_list = [self.net_label.text]
            print(properties["Filename"],type(properties["Filename"]))
            self.analysis.dictionary.update({properties["Filename"]: temp_list})
        print('Added following result to collection: ',result.get_object_properties_list())

    def lung_segment_kmeans(self):
        try:
            segment = self.image_object.get_segmented_lungs()
            plt.imshow(segment, cmap='gray')
            plt.axis('off')
            plt.show()
        except Exception as ex:
            print(ex)

    def show_load(self):
        """This function runs load dialog"""
        
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        """This function runs save dialog"""
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()



    def get_file_format(self, filename):
        """This function decides on the displayed image format"""
        if filename.endswith('.dcm'):
            return ImageType.DCM
        elif filename.endswith('.nii'):
            return ImageType.NIFTI
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            return ImageType.JPG
        elif filename.endswith('.png'):
            return ImageType.PNG

    def load(self, path, filename):
        """This function runs the load process for an image selected in the load dialog"""
        image_folder = path
        image_file_name = str(Path(filename[0]).name)

        file_type = self.get_file_format(image_file_name)

        if file_type == ImageType.DCM:
            self.image_object = DicomImage(image_folder, image_file_name)
        elif file_type == ImageType.NIFTI:
            self.image_object = NiftiImage(image_folder, image_file_name)
        elif file_type == ImageType.JPG:
            self.image_object = JpgImage(image_folder, image_file_name)
        elif file_type == ImageType.PNG:
            self.image_object = PngImage(image_folder, image_file_name)

        if self.result is not None:
            self.left_panel.remove_widget(self.result)

        self.left_panel.remove_widget(self.plot)
        self.plot = MyFigure(image_data=self.image_object.get_current_slice())
        self.left_panel.add_widget(self.plot)
        self.slider.value = 0
        self.slider.step = 1
        self.slider.range = (0, self.image_object.total_slice_number-1)
        self.slider.value_track = True

        self.slices_info.text = "Slice: {0}/{1}".format(self.image_object.current_slice_number+1,
                                                        self.image_object.total_slice_number)
        self.dismiss_popup()
        # new analysis initialization
        self.analysis = Analysis(slices_number=self.image_object.total_slice_number)

    def get_root_path_for_load_dialog(self):
        """This function gets the root folder for load dialog"""
        return str(Path(r"C:\Users\Maya\studia\4rok\inz\covidSeg"))

    def save(self, path, filename):
        """This function runs the saving process after pressing 'Save anonymized file' button"""
        success = self.image_object.save_anonymized_file(filename, path)
        if success:
            print('File saved')
        else:
            print('File not saved')
        self.dismiss_popup()

    def show_analysis_popup(self):

        if(self.analysis_popup is not None):
            self.current_model = self.analysis_popup.current_model
        self.analysis_popup = Factory.AnalysisDialog(self.analysis,self.image_object,self.current_model)
        print(self.current_model)
        if(self.current_model is None):
            self.analysis_popup.box_layout.add_widget(Label(text='None yet!'),index=9)
        else:
            bl = BoxLayout(orientation='horizontal')
            bl.add_widget(Label(text=str(type(self.current_model).__name__)))
            bl.add_widget(Button(text='Classify',on_release=self.analysis_popup.analysis_classify_recent))
            self.analysis_popup.box_layout.add_widget(bl,index=9)
        self.analysis_popup.open()

    

    def show_result_popup(self):
        """
        Function creates adn show PopUp in application with some data about image.
        :return: None
        """
        properties = self.image_object.get_info()
        # grid = GridLayout(cols=2,
        #                   row_force_default=True,
        #                   row_default_height=20,size_hint_y=None)
        # for key, value in properties.items():
        #     prop_name = Label(text=(key+":"), size_hint_x=None, size_hint_y=None,halign='justify')
        #     prop_value = Label(text=str(value),halign='justify',size_hint_y=None)
        #     prop_name.bind(size=prop_name.setter('text_size'))
        #     prop_value.bind(size=prop_value.setter('text_size'))
        #     grid.add_widget(prop_name)
        #     grid.add_widget(prop_value)
        # for key, value in properties.items():
        #     prop_name = Label(text=(key+":"), size_hint_x=None, size_hint_y=None,halign='justify')
        #     prop_value = Label(text=str(value),halign='justify',size_hint_y=None)
        #     prop_name.bind(size=prop_name.setter('text_size'))
        #     prop_value.bind(size=prop_value.setter('text_size'))
        #     grid.add_widget(prop_name)
        #     grid.add_widget(prop_value)
        
        popup = Factory.ResultPopup(analysis = self.analysis)
        if(self.analysis is None):
            popup.scroll_view.text+='No analysis made yet'
        else:
            for result in self.analysis.result_list:
                res = result.get_object_properties_list()
                string ='File name: '+ res[0]+"    Result: "+res[5]+'    Method: '+result.get_method_name()+'\n'
                popup.scroll_view.text+=string
        #popup.scroll_view.add_widget(grid, index=0)
        popup.open()

    # def __init__(self, *args, **kwargs):
    #     super(RootWidget, self).__init__(*args, **kwargs)



class Main(App):
    pass


# Factory.register('RootWidget', cls=RootWidget)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    Main().run()
