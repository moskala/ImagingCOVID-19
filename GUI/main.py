# Kivy imports
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

# Custom kivy widgets imports
from CustomKivyWidgets.DialogWidgets import LoadDialog, SaveDialog
from CustomKivyWidgets.ShowImageWidget import MyFigure, START_IMAGE
from CustomKivyWidgets.DrawLesionsWidgets import DrawPopup, DrawFigure
from CustomKivyWidgets.ResultPopupWidget import ResultPopup

# Python imports
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
from Grayscale import *
from Analysis.Analysis import *
from Analysis.Result import *

# Paths
GUI_FOLDER = str(Path().resolve())
MY_FOLDER = Path()
MODEL_PATH = str(Path().resolve().parent.parent / "models" / "best_checkpoint.pth")
MODEL_GLCM_PATH = str(Path().resolve().parent.parent / "models" / "glcmModelFitFinal.joblib")
MODEL_ALEX_EXTRACT_PATH = str(Path().resolve().parent.parent / "models" / "featureExtraction.joblib")
# MODEL_ALEX_EXTRACT = load(MODEL_ALEX_EXTRACT_PATH)
MODEL_ALEX_DATA_PATH = str(Path().resolve().parent.parent / "models" / "csPrePCAFeatures50.joblib")
# MODEL_ALEX_DATA = load(MODEL_ALEX_DATA_PATH)
MODEL_ALEX_SVM_PATH = str(Path().resolve().parent.parent / "models" / "alexnetModel50.joblib")
# MODEL_ALEX_SVM = load(MODEL_ALEX_SVM_PATH)
MODEL_HARALICK_PATH = str(Path().resolve().parent.parent / "models" / "haralickSVM.joblib")



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
        """not implemented yet"""
        pass

    def layer_selection(self):
        number = self.image_object.current_slice_number
        if number in self.selected_layers:
            self.selected_layers.remove(number)
        else:
            self.selected_layers.append(number)
        self.set_layers_button()
        print(self.selected_layers)

    def set_layers_button(self):
        if self.image_object.current_slice_number in self.selected_layers:
            self.add_remove_layer.text = "Remove slice\nfrom analysis"
        else:
            self.add_remove_layer.text = "Add slice\nto analysis"

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

    def dismiss_popup(self):
        """This function closes popup windows"""
        self._popup.dismiss()

    def neural_network(self):
        """This function runs the neural network process for the displayed image"""
        if self.image_object.file_type == ImageType.JPG or self.image_object.file_type == ImageType.PNG:
            self.net_label.text = Net.testImage(self.image_object.get_file_path(), MODEL_PATH)
        else:
            self.net_label.text = "Network accepts only jpg or png files!"

    def glcm(self):
        """Classification using GLCM method."""
        try:
            prediction = PredictGLCM(self.image_object.src_folder,self.image_object.src_filename, MODEL_GLCM_PATH)
            print(prediction)
            if prediction[0] == 'normal':
                self.net_label.text = "Normal"
            else:
                self.net_label.text = "COVID-19"
        except Exception as error:
            print(error)
        self.add_result_to_analysis(False)
    
    def alexnet(self):
        """Classification using Alexnet method."""
        try:
            prediction = PredictAlex(self.image_object.src_folder,
                                     self.image_object.src_filename,
                                     MODEL_ALEX_EXTRACT_PATH,
                                     MODEL_ALEX_DATA_PATH,
                                     MODEL_ALEX_SVM_PATH)
            print(prediction)
            if prediction[0] == 'normal':
                self.net_label.text = "Normal"
            else:
                self.net_label.text = "COVID-19"
        except Exception as error:
            print(error)
        self.add_result_to_analysis(True)

    def haralick(self):
        prediction = PredictHaralick(self.image_object.src_folder,self.image_object.src_filename, MODEL_HARALICK_PATH)
        print(prediction)
        if(prediction[0]=='normal'):
            self.net_label.text = "Normal"
        else:
            self.net_label.text = "COVID-19"
        self.add_result_to_analysis(False)

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

    def save(self, path, filename):
        """This function runs the saving process after pressing 'Save anonymized file' button"""
        success = self.image_object.save_anonymized_file(filename, path)
        if success:
            print('File saved')
        else:
            print('File not saved')
        self.dismiss_popup()

    def show_result_popup(self):
        """
        Function creates adn show PopUp in application with some data about image.
        :return: None
        """
        properties = self.image_object.get_info()
        grid = GridLayout(cols=2,
                          row_force_default=True,
                          row_default_height=40,
                          padding=[2, 2, 2, 2],
                          spacing=[10, 5])
        for key, value in properties.items():
            prop_name = Label(text=(key+":"), size_hint_x=None, width=200, halign='right')
            prop_value = Label(text=str(value))
            prop_name.bind(size=prop_name.setter('text_size'))
            prop_value.bind(size=prop_value.setter('text_size'))
            grid.add_widget(prop_name)
            grid.add_widget(prop_value)
        popup = Factory.ResultPopup(analysis=self.analysis)
        popup.content.add_widget(grid, index=1, canvas='before')
        popup.open()

    def __init__(self, *args, **kwargs):
        super(RootWidget, self).__init__(*args, **kwargs)
        print("Create root")
        self.selected_layers = []


class Main(App):
    pass


Factory.register('RootWidget', cls=RootWidget)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    Main().run()
