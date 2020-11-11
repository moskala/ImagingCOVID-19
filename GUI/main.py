import matplotlib
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

matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

sys.path.append(str(Path().resolve().parent / "Methods"))
from Anonymize import Anonymization_Functions
from LungSegmentation.LungSegmentation_MethodA_dicom import SegmentationA
from LungSegmentation.LungSegmentation_MethodB_dicom import SegmentationB
import Show_matplotlib_all as show


MY_FOLDER = Path()


class MyFigure(FigureCanvasKivyAgg):

    def __init__(self, val=0, image_data=None, **kwargs):
        if image_data is None:
            image_data = show.get_plot_data_jpg_png('sample_image.jpg')
        plt.axis('off')
        plt.imshow(image_data, cmap='gray')
        super(MyFigure, self).__init__(plt.gcf(), **kwargs)
        # self.howMany = len(test_patient_images)
        self.curPlt = plt.gcf()
        # self.image = test_patient_images[val]
        # self.scan = test_patient_scans[val]
        # self.path = INPUT_FOLDER
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
    current_val = 0
    plot = None
    result = None
    label_info = "hello2"
    image_type_plain = False
    image_type_dicom = False
    image_type_nii = False
    image_path = ""
    image_folder = ""

    _popup = None

    # def slider_changed_value(self, value):
    #     slice_number = self.current_val + int(value)
    #
    #     if slice_number < 0:
    #         slice_number = 0
    #
    #     self.current_val = slice_number
    #
    #     if self.plot is not None and self.plot.howMany >= slice_number:
    #         self.dicom_viewer.remove_widget(self.plot)
    #         self.plot = MyFigure(slice_number)
    #         self.dicom_viewer.add_widget(self.plot)
    #         self.slide_number.text = str(slice_number)

    def dismiss_popup(self):
        self._popup.dismiss()

    def lung_segment_binary(self):
        sgmB = SegmentationB()
        ct_scan = sgmB.read_ct_scan(self.image_folder)
        segmented_ct_scan = sgmB.segment_lung_from_ct_scan(ct_scan, self.plot.val)
        # sgmB.plot_ct_scan(segmented_ct_scan,self.plot.val)
        # test = sgmB.get_segmented_lungs(self.img.getdata())
        # plt.imshow(segmented_ct_scan,cmap='gray')
        plt.imshow(segmented_ct_scan, cmap='gray')
        plt.show()

    # Chciałam tutaj żeby się nowy widget dodawał ale na razie nie działa
    def lung_segment_binary_add_widget(self):

        if self.image_type_dicom is not True:
            print("This method is only for dicom files for now.")
            return

        sgmB = SegmentationB()
        # ct_scan = sgmB.read_ct_scan(self.plot.path)
        ct_scan = sgmB.read_ct_scan(self.image_folder)
        segmented_ct_scan = sgmB.segment_lung_from_ct_scan(ct_scan, self.plot.val)
        # sgmB.plot_ct_scan(segmented_ct_scan,self.plot.val)
        # test = sgmB.get_segmented_lungs(self.img.getdata())
        plt.imshow(segmented_ct_scan, cmap='gray')
        plt.show()
        # if self.result is not None:
        #     self.left_panel.remove_widget(self.result)
        #
        # self.result = MyFigure(image_data=segmented_ct_scan)
        # self.left_panel.add_widget(self.result)


    def lung_segment_watershed(self):
        print("lung_segment_watershed")
        print(self.image_type_dicom)
        if self.image_type_dicom is not True:
            print("This method is only for dicom files for now.")
            return

        # img = self.plot
        sgm = SegmentationA()
        test_patient_scans = sgm.load_scan(self.image_folder)
        test_patient_images = sgm.get_pixels_hu(test_patient_scans)
        img = sgm.preprocess_image(self.image_path)
        test_segmented, _ = sgm.seperate_lungs(img)
        # test_segmented, test_lungfilter, test_outline, test_watershed, test_sobel_gradient, test_marker_internal, \
        #     test_marker_external, test_marker_watershed = sgm.seperate_lungs(img)
        # print ("Segmented Lung")
        plt.imshow(test_segmented, cmap='gray')
        # plt.imshow(test_segmented)
        plt.show()
        # if self.result is not None:
        #     self.left_panel.remove_widget(self.result)
        #
        # self.result = MyFigure(image_data=test_segmented)
        # self.left_panel.add_widget(self.result)
        # print("lung_segment_watershed")

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

    def set_format(self, dicom, nii, plain):
        self.image_type_dicom = False
        self.image_type_nii = False
        self.image_type_plain = False

        if dicom:
            self.image_type_dicom = True
        elif nii:
            self.image_type_nii = True
        else:
            self.image_type_plain = True

    def load(self, path, filename):

        self.image_path = filename[0]
        self.image_folder = path
        filename = str(Path(filename[0]).name)
        # print(filename)
        # print(path)
        if self.result is not None:
            self.left_panel.remove_widget(self.result)

        if filename.endswith('.jpg') or filename.endswith('.png'):
            self.set_format(False, False, True)
            anonymous_file = Anonymization_Functions.anonymize_png_jpg(filename, path, 'temp')
            plot_data = show.get_plot_data_jpg_png(anonymous_file)

        elif filename.endswith('.nii'):
            self.set_format(False, True, False)
            anonymous_file = Anonymization_Functions.anonymize_nii(filename, path, 'temp')
            plot_data = show.get_plot_data_nii(anonymous_file, 0)

        elif filename.endswith('.dcm') or filename.endswith('.DCM'):
            self.set_format(True, False, False)
            anonymous_file = Anonymization_Functions.anonymize_dicom(filename, path, 'temp')
            plot_data = show.get_plot_data_dicom(anonymous_file)

        else:
            print("Not supported file format")
            return

        self.left_panel.remove_widget(self.plot)
        self.plot = MyFigure(image_data=plot_data)
        self.left_panel.add_widget(self.plot)
        self.dismiss_popup()


class Main(App):
    pass


# Factory.register('RootWidget', cls=RootWidget)
Factory.register('LoadDialog', cls=LoadDialog)
# Factory.register('SaveDialog', cls=SaveDialog)
# Factory.register('Picture', cls=SaveDialog)

if __name__ == '__main__':
    Main().run()
