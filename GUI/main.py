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

matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

sys.path.append(str(Path().resolve().parent / "Methods"))
from Anonymize import Anonymization_Functions
from LungSegmentation.LungSegmentation_MethodA_dicom import SegmentationA
from LungSegmentation.LungSegmentation_MethodB_dicom import SegmentationB
import Show_matplotlib_all as show


MY_FOLDER = Path()


class ImageViewer:

    slices = []
    slice_no = 0
    current_slice = None

    def __init__(self, slices, value, current_slice=""):
        self.slices = slices
        self.slice_no = value
        self.current_slice = current_slice

    def get_current_slice(self):
        self.current_slice = self.slices[self.slice_no]
        return self.current_slice

    def get_next_slice(self, value):
        max_len = len(self.slices)

        if value >= max_len:
            self.slice_no = max_len - 1
        elif value <= 0:
            self.slice_no = 0
        else:
            self.slice_no = value
        print(self.slice_no)
        return self.slices[self.slice_no]


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
    slider = None
    label_info = "hello2"
    image_type_plain = False
    image_type_dicom = False
    image_type_nii = False
    image_path = ""
    image_folder = ""

    image_viewer = None

    _popup = None

    def automatic_layer_choice(self):
        pass

    def slider_changed_value(self, value):
        slice_no = int(value)
        if self.plot is not None and self.image_viewer is not None:
            self.left_panel.remove_widget(self.plot)
            self.plot = MyFigure(image_data=self.image_viewer.get_next_slice(slice_no))
            self.left_panel.add_widget(self.plot)

    def load_next_slice(self, value):
        diff = int(value)

        if self.plot is not None and self.image_viewer is not None:
            slice_no = self.image_viewer.slice_no + diff
            self.left_panel.remove_widget(self.plot)
            self.plot = MyFigure(image_data=self.image_viewer.get_next_slice(slice_no))
            self.left_panel.add_widget(self.plot)



    def dismiss_popup(self):
        self._popup.dismiss()

    def lung_segment_binary(self):

        if self.image_type_dicom is not True:
            print("This method is only for dicom files for now.")
            return

        print(self.image_folder)
        ct_scan = SegmentationB.read_ct_scan(self.image_folder)
        segmented_ct_scan = SegmentationB.segment_lung_from_ct_scan(ct_scan, int(self.slid.value))
        print(segmented_ct_scan)
        # return
        plt.figure()
        plt.imshow(segmented_ct_scan, cmap='gray')
        plt.axis('off')
        plt.show()

    def lung_segment_watershed(self):

        print(self.image_type_dicom)
        if self.image_type_dicom is not True:
            print("This method is only for dicom files for now.")
            return

        print(self.image_folder)
        slices = SegmentationA.load_scan(self.image_folder)
        arr = SegmentationA.get_pixels_hu(slices)
        test_segmented, test_lungfilter, test_outline, test_watershed, test_sobel_gradient, test_marker_internal, \
            test_marker_external, test_marker_watershed = SegmentationA.seperate_lungs(arr[int(self.slid.value)])
        print(test_segmented)
        # return
        plt.figure()
        plt.imshow(test_segmented, cmap='gray')
        plt.axis('off')
        plt.show()

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
            self.image_viewer = ImageViewer([plot_data], 0)

        elif filename.endswith('.nii'):
            self.set_format(False, True, False)
            anonymous_file = Anonymization_Functions.anonymize_nii(filename, path, 'temp')
            # plot_data = show.get_plot_data_nii(anonymous_file, 0)
            self.image_viewer = ImageViewer(show.get_plot_data_nii_all(anonymous_file), 0)

        elif filename.endswith('.dcm') or filename.endswith('.DCM'):
            self.set_format(True, False, False)
            anonymous_file = Anonymization_Functions.anonymize_dicom(filename, path, 'temp')
            #plot_data = show.get_plot_data_dicom(anonymous_file)
            self.image_viewer = ImageViewer(show.get_plot_data_dicom_all(self.image_folder), 0)

        else:
            print("Not supported file format")
            return
        # if self.slider is not None:
        #     self.left_panel.remove_widget(self.slider)
        self.left_panel.remove_widget(self.plot)
        self.plot = MyFigure(image_data=self.image_viewer.get_current_slice())
        self.left_panel.add_widget(self.plot)
        self.ids.side = Slider(min=0, max=len(self.image_viewer.slices), step=1, id="slid", value=0)
        self.ids.side.value = 0
        # self.left_panel.add_widget(self.slider)
        self.dismiss_popup()


class Main(App):
    pass


# Factory.register('RootWidget', cls=RootWidget)
Factory.register('LoadDialog', cls=LoadDialog)
# Factory.register('SaveDialog', cls=SaveDialog)
# Factory.register('Picture', cls=SaveDialog)

if __name__ == '__main__':
    Main().run()
