import matplotlib
# matplotlib.use('Agg', force=True)  # comment this line to see effect
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.core.image import Image as CoreImage
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.slider import Slider
import pydicom
from pathlib import Path
import sys
import os
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
# matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

sys.path.append(str(Path().resolve().parent / "Methods"))

from LungSegmentation.LungSegmentation_MethodA_dicom import SegmentationA
from LungSegmentation.LungSegmentation_MethodB_dicom import SegmentationB
import LungSegmentation.LungSegmentation_MethodKMeans_AllTypes as segmentation
import Show_matplotlib_all as show
from ImageClass import *
from net.testNet import Net
from PredictGLCM import *
from PredictAlexnet import *


MY_FOLDER = Path()
MODEL_PATH = str(Path().resolve().parent.parent / "models" / "best_checkpoint.pth")
MODEL_GLCM_PATH = str(Path().resolve().parent.parent / "models" / "glcmModelFitFinal.joblib")
MODEL_ALEX_EXTRACT_PATH = str(Path().resolve().parent.parent / "models" / "featureExtraction.joblib")
MODEL_ALEX_DATA_PATH = str(Path().resolve().parent.parent / "models" / "csPrePCAFeatures.joblib")
MODEL_ALEX_SVM_PATH = str(Path().resolve().parent.parent / "models" / "alexnetModel.joblib")
GUI_FOLDER = str(Path().resolve())
START_IMAGE = "sample_image.jpg"


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
        self.val = val


class LoadDialog(FloatLayout):
    """This class is used to run the load dialog"""
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    """This class is used to run the save dialog"""
    save = ObjectProperty(None)
    img = ObjectProperty(None)
    cancel = ObjectProperty(None)


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
    

    def automatic_layer_choice(self):
        """not implemented yet"""
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
        popup = Factory.ResultPopup()
        popup.content.add_widget(grid, index=1, canvas='before')
        popup.open()


class Main(App):
    pass


# Factory.register('RootWidget', cls=RootWidget)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    Main().run()
