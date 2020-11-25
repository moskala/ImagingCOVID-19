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

# matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

sys.path.append(str(Path().resolve().parent / "Methods"))

from LungSegmentation.LungSegmentation_MethodA_dicom import SegmentationA
from LungSegmentation.LungSegmentation_MethodB_dicom import SegmentationB
import Show_matplotlib_all as show
from ImageClass import *
from net.testNet import Net


MY_FOLDER = Path()
MODEL_PATH = r"D:\Studia\sem7\inzynierka\sieci\Contrastive-COVIDNet\saved\best_checkpoint.pth"
GUI_FOLDER = r"D:\Studia\sem7\inzynierka\aplikacja\ImagingCOVID-19\GUI"
START_IMAGE = "sample_image.jpg"


class MyFigure(FigureCanvasKivyAgg):

    def __init__(self, val=0, image_data=None, **kwargs):
        if image_data is None:
            image_data = show.get_plot_data_jpg_png('sample_image.jpg')
        plt.axis('off')
        plt.imshow(image_data, cmap='gray')
        super(MyFigure, self).__init__(plt.gcf(), **kwargs)
        # self.howMany = len(test_patient_images)
        self.curPlt = plt.gcf()
        self.val = val


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    img = ObjectProperty(None)
    cancel = ObjectProperty(None)


class RootWidget(FloatLayout):

    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    image = ObjectProperty(None)
    slider_val = ObjectProperty(None)

    plot = None
    result = None
    # slider = None

    image_object = JpgImage(GUI_FOLDER, START_IMAGE)

    _popup = None

    def automatic_layer_choice(self):
        pass

    def slider_changed_value(self, value):
        slice_number = int(value)
        if self.plot is not None and self.image_object is not None:
            self.left_panel.remove_widget(self.plot)
            self.plot = MyFigure(image_data=self.image_object.get_next_slice(slice_number))
            self.left_panel.add_widget(self.plot)
            self.slices_info.text = "Slice: {0}/{1}".format(self.image_object.current_slice_number+1,
                                                            self.image_object.total_slice_number)

    def load_next_slice(self, value):
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
        self._popup.dismiss()

    def neural_network(self):

        if self.image_object.file_type == ImageType.JPG or self.image_object.file_type == ImageType.PNG:
            self.net_label.text = Net.testImage(self.image_object.get_file_path(), MODEL_PATH)
        else:
            self.net_label.text = "Network accepts only jpg or png files!"

    def lung_segment_binary(self):

        try:
            if self.image_object.file_type != ImageType.DCM:
                print("This method is only for dicom files for now.")
                return
            image_folder = self.image_object.src_folder

            ct_scan = SegmentationB.read_ct_scan(image_folder)
            segmented_ct_scan = SegmentationB.segment_lung_from_ct_scan(ct_scan, 0)

            plt.figure()
            plt.imshow(segmented_ct_scan, cmap='gray')
            plt.axis('off')
            plt.show()
        except Exception as ex:
            print(ex)

    def lung_segment_watershed(self):

        try:
            if self.image_object.file_type != ImageType.DCM:
                print("This method is only for dicom files for now.")
                return

            image_folder = self.image_object.src_folder
            slices = SegmentationA.load_scan(image_folder)
            arr = SegmentationA.get_pixels_hu(slices)
            test_segmented, test_lungfilter, test_outline, test_watershed, test_sobel_gradient, test_marker_internal, \
                test_marker_external, test_marker_watershed = SegmentationA.seperate_lungs(arr[0])

            plt.figure()
            plt.imshow(test_segmented, cmap='gray')
            plt.axis('off')
            plt.show()
        except Exception as ex:
            print(ex)

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def get_file_format(self, filename):
        if filename.endswith('.dcm'):
            return ImageType.DCM
        elif filename.endswith('.nii'):
            return ImageType.NIFTI
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            return ImageType.JPG
        elif filename.endswith('.png'):
            return ImageType.PNG

    def load(self, path, filename):

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
        return str(Path(r"D:\Studia\sem7\inzynierka\aplikacja\test_data"))

    def save(self, path, filename):
        success = self.image_object.save_anonymized_file(filename, path)
        if success:
            print('File saved')
        else:
            print('File not saved')
        self.dismiss_popup()


class Main(App):
    pass


# Factory.register('RootWidget', cls=RootWidget)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)
# Factory.register('Picture', cls=SaveDialog)

if __name__ == '__main__':
    Main().run()
