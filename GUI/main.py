# Kivy imports
from kivy.app import App
# from kivy.uix.togglebutton import ToggleButton
# from kivy.uix.widget import Widget
# from kivy.uix.floatlayout import FloatLayout
# from kivy.properties import ObjectProperty
# from kivy.uix.popup import Popup
# from kivy.uix.scrollview import ScrollView
# from kivy.core.window import Window
# from kivy.logger import Logger
# from kivy.uix.scatter import Scatter
# from kivy.uix.slider import Slider
# from kivy.factory import Factory
# from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

# Custom kivy widgets imports
from CustomKivyWidgets.DialogWidgets import LoadDialog, SaveDialog
from CustomKivyWidgets.ShowImageWidget import MyFigure, START_IMAGE
from CustomKivyWidgets.DrawLesionsWidgets import DrawPopup, DrawFigure
from CustomKivyWidgets.ResultPopupWidget import ResultPopup
from CustomKivyWidgets.AnalysisPopup import AnalysisPopup
from CustomKivyWidgets.LungSegmentationPopup import LungSegmentationPopup
from CustomKivyWidgets.LayersPopup import LayersPopup

# Python imports
import matplotlib.pyplot as plt
import csv
from joblib import load
import imageio
from datetime import date
from pathlib import Path
import sys
sys.path.append(str(Path().resolve().parent / "Methods"))

# Implemented methods imports
from LungSegmentation.LungSegmentation_MethodA_dicom import SegmentationA
from LungSegmentation.LungSegmentation_MethodB_dicom import SegmentationB
import LungSegmentation.LungSegmentationUtilities as segmentUtils
from ImageClass import ImageType, ImageObject, JpgImage, PngImage, DicomImage, NiftiImage
from net.testNet import Net
from PredictGLCM import *
from PredictAlexnet import *
from PredictHaralick import *
from PredictGlcmHaralick import *
from ChooseSlices import LayerChoice, LayerChoiceType
from Grayscale import *
from Analysis.Analysis import *
from Analysis.Result import *

# Paths
GUI_FOLDER = str(Path().resolve())
MY_FOLDER = Path()



class RootWidget(FloatLayout):
    """This class contains the root element for gui and all the necessary methods"""
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    image = ObjectProperty(None)
    result_grid = ObjectProperty(None)

    plot = None
    result = None

    image_object = JpgImage(GUI_FOLDER, START_IMAGE)

    _popup = None
    _draw_figure = None
    analysis = None

    current_model = None
    analysis_popup = None
    layers_popup = None

    layer_choice = LayerChoice()

    def draw_lesions(self):
        """
        Function creates draw lesions popup and binds needed functions.
        :return: None
        """
        try:
            self._draw_figure = None
            popup = Factory.DrawPopup()
            popup.title = self.image_object.src_filename
            box = popup.ids.draw_panel
            fig = DrawFigure(image_data=self.image_object.get_current_slice())
            box.add_widget(fig, canvas='before')
            popup.ids.add_region_button.bind(on_release=fig.add_new_region)
            popup.ids.delete_region_button.bind(on_release=fig.delete_current_region)
            popup.bind(on_dismiss=self.get_marked_lesions)
            self._draw_figure = fig
            popup.open()
        except Exception as error:
            print(error)

    def get_marked_lesions(self, *args):
        """
        Function is called when draw popup is being dismissed.
        Function reads coordinates of marked lesions from drawing figure.
        :param args: arguments passed by on_dismiss callback
        :return:
        """
        try:
            regions = self._draw_figure.finish_drawing()
            res = segmentUtils.fill_selected_regions_on_mask(self.image_object.get_size(), regions)
            self._draw_figure = None
            res = segmentUtils.flip_mask_vertically(res)
            # TODO zamiast wyświetlania zrobić analizę
            plt.imshow(res, cmap='gray')
            plt.show()
        except Exception as error:
            print(error)

    def automatic_layer_choice(self):
        self.layers_popup = Factory.LayersPopup(self.layer_choice)
        self.layers_popup.open()

    def save_layer_selection(self, *args):
        settings = self.layers_popup.get_settings()
        if settings is not None:
            self.layer_choice = settings
            self.layers_popup.dismiss()

    def layer_selection(self):
        number = self.image_object.current_slice_number
        if self.layer_choice.check_collection_layer(number):
            self.layer_choice.remove_collection_layer(number)
        else:
            self.layer_choice.append_collection_layer(number)
        self.set_layers_button()

    def set_layers_button(self):
        if self.layer_choice.check_collection_layer(self.image_object.current_slice_number):
            self.add_remove_layer.text = "Remove layer\nfrom analysis"
        else:
            self.add_remove_layer.text = "Add layer\nto analysis"

    def reset_layers_choice(self):
        self.layer_choice = LayerChoice()
        self.set_layers_button()

    def slider_changed_value(self, value):
        """This function changes the displayed image when the slider is moved"""
        slice_number = int(value)
        if self.plot is not None and self.image_object is not None:
            self.left_panel.remove_widget(self.plot)
            self.plot = MyFigure(image_data=self.image_object.get_next_slice(slice_number))
            self.left_panel.add_widget(self.plot)
            self.slices_info.text = "Slice: {0}/{1}".format(self.image_object.current_slice_number+1,
                                                            self.image_object.total_slice_number)
            self.set_layers_button()
            self.layer_choice.update_choice_singular(self.image_object.current_slice_number)

    def load_specific_slice(self,which_slice):
        if self.plot is not None and self.image_object is not None:
            slice_number = int(which_slice)
            self.left_panel.remove_widget(self.plot)
            self.plot = MyFigure(image_data=self.image_object.get_specific_slice(slice_number))
            self.left_panel.add_widget(self.plot)
            self.slices_info.text = "Slice: {0}/{1}".format(which_slice,
                                                            self.image_object.total_slice_number)
            #update image object in root widget
            self.image_object.get_specific_slice(slice_number)
            self.slider.value = self.image_object.current_slice_number
            self.layer_choice.update_choice_singular(self.image_object.current_slice_number)

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
            self.set_layers_button()
            self.layer_choice.update_choice_singular(self.image_object.current_slice_number)

    def dismiss_popup(self):
        """This function closes popup windows"""
        self._popup.dismiss()

    def neural_network(self):
        """This function runs the neural network process for the displayed image"""
        if self.image_object.file_type == ImageType.JPG or self.image_object.file_type == ImageType.PNG:
            self.net_label.text = Net.testImage(self.image_object.get_file_path(), MODEL_PATH)
        else:
            self.net_label.text = "Network accepts only jpg or png files!"

    def lung_tissue_segmentation(self):
        popup = LungSegmentationPopup(self.image_object)
        popup.open()
        plt.close('all')
        # self.load_specific_slice(self.image_object.current_slice_number)


    def add_result_to_analysis(self,isAlex,prediction,slic):
        properties = self.image_object.get_info()
        if(isAlex):
            result = AlexnetResult(prediction,slic,properties["Height"],properties["Width"],properties["CT Window Type"],properties["Filename"])
        else:
            result = HaralickGlcmResult(prediction,slic,properties["Height"],properties["Width"],properties["CT Window Type"],properties["Filename"])
        self.analysis.add_to_list(result)
        #dict
        if(properties["Filename"] in self.analysis.dictionary):
            self.analysis.dictionary[properties["Filename"]].append(prediction)
        else:
            temp_list = [prediction]
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
        # new layer choice initialization
        self.reset_layers_choice()


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
        self.analysis_popup = Factory.AnalysisPopup(self.analysis,self.image_object,self.current_model)
        print(self.current_model)
        if(self.current_model is None):
            self.analysis_popup.box_layout.add_widget(Label(text='None yet!'),index=9)
        else:
            bl = BoxLayout(orientation='horizontal')
            bl.add_widget(Label(text=str(type(self.current_model).__name__)))
            bl.add_widget(Button(text='Classify',on_release=self.analysis_popup.analysis_classify_recent))
            self.analysis_popup.box_layout.add_widget(bl,index=9)
        self.analysis_popup.open()
        self.current_model =self.analysis_popup.current_model



    def show_result_popup(self):
        """
        Function creates adn show PopUp in application with some data about image.
        :return: None
        """
        properties = self.image_object.get_info()
        popup = Factory.ResultPopup(analysis = self.analysis)
        if(self.analysis is None):
            popup.scroll_view.text+='No analysis made yet'
        else:
            for result in self.analysis.result_list:
                res = result.get_object_properties_list()
                string ='File name: '+ res[0]+"    Result: "+res[3]+'    Method: '+result.get_method_name()+'\n'
                popup.scroll_view.text+=string
        popup.open()

    def __init__(self, *args, **kwargs):
        super(RootWidget, self).__init__(*args, **kwargs)
        print("Create root")
        self.image_object = JpgImage(GUI_FOLDER, START_IMAGE)


class Main(App):
    pass


Factory.register('RootWidget', cls=RootWidget)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    Main().run()
