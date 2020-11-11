import matplotlib
# garden install matplotlib xd w maja/.kivy - to sie dzieje tylko raz, nie wiem o co chodzi xd
# matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
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
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg


from pathlib import Path
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("Anonimization_StrigOffMetaData_png_jpg.py"))))
from Anonimization_StrigOffMetaData_png_jpg import Anonymize
from pathlib import Path, PurePath
import sys
import os


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(CURRENT_DIR), "Methods"))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("Anonimization_StrigOffMetaData_png_jpg.py"))))

from Anonimization_StrigOffMetaData_png_jpg import Anonymize
from LungSegmentation_MethodA_dicom import SegmentationA

sys.path.append(os.path.join(os.path.dirname(CURRENT_DIR),"Methods"))
from LungSegmentation.LungSegmentation_MethodA_dicom import SegmentationA
from LungSegmentation.LungSegmentation_MethodB_dicom import SegmentationB


import pydicom
MY_FOLDER = Path(r'D:/Studia/sem7/inzynierka/aplikacja/ImagingCOVID-19/dicom test/cancer_files')


class MyFigure(FigureCanvasKivyAgg):

    def __init__(self, val=0, INPUT_FOLDER=MY_FOLDER, **kwargs):
        sg = SegmentationA()
        test_patient_scans = sg.load_scan(INPUT_FOLDER)
        test_patient_images = sg.get_pixels_hu(test_patient_scans)
        plt.axis('off')
        plt.imshow(test_patient_images[val], cmap='gray')
        super(MyFigure, self).__init__(plt.gcf(), **kwargs)
        self.howMany = len(test_patient_images)
        self.curPlt = plt.gcf()
        self.image = test_patient_images[val]
        self.scan = test_patient_scans[val]
        self.path = INPUT_FOLDER
        self.val = val
        self.dicom = pydicom.read_file(os.path.join(INPUT_FOLDER,os.listdir(INPUT_FOLDER)[val]))

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

    _popup = None

    def slider_changed_value(self, value):
        slice_number = self.current_val + int(value)

        if slice_number < 0:
            slice_number = 0

        self.current_val = slice_number

        if self.plot is not None and self.plot.howMany >= slice_number:
            self.dicom_viewer.remove_widget(self.plot)
            self.plot = MyFigure(slice_number)
            self.dicom_viewer.add_widget(self.plot)
            self.slide_number.text = str(slice_number)

    def dismiss_popup(self):
        self._popup.dismiss()

    def lung_segment_binary(self):
        sgmB = SegmentationB()
        ct_scan = sgmB.read_ct_scan(self.plot.path)
        segmented_ct_scan = sgmB.segment_lung_from_ct_scan(ct_scan,self.plot.val)
        # sgmB.plot_ct_scan(segmented_ct_scan,self.plot.val)
        # test = sgmB.get_segmented_lungs(self.img.getdata())
        # plt.imshow(segmented_ct_scan,cmap='gray')
        plt.imshow(segmented_ct_scan,cmap='gray')
        plt.show()

    def lung_segment_watershed(self):
        sgm = SegmentationA()
        img = self.plot.image
        test_segmented, test_lungfilter, test_outline, test_watershed, test_sobel_gradient, test_marker_internal, test_marker_external, test_marker_watershed = sgm.seperate_lungs(img)
        # print ("Segmented Lung")
        plt.imshow(test_segmented, cmap='gray')
        # plt.imshow(test_segmented)
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
    
    def load(self, path, filename):
        # self.image = CoreImage(os.path.join(path, filename[0]))
        # try:
        # load the image
        # picture = Image(source=os.path.join(path, filename[0]))
        # add to the main field
        # self.add_widget(picture)
        # except Exception as e:
        # Logger.exception('Pictures: Unable to load <%s>' % filename)
        anonym = Anonymize()
        
        if len(path) > 0 and len(filename) == 0:
            print(path)
            self.photos.remove_widget(self.plot)
            self.plot = MyFigure(INPUT_FOLDER=path)
            self.photos.add_widget(self.plot)
            # self.slid.max = len(os.listdir(path))
        else:
            newFile = anonym.MetadataStrip(os.path.join(path, filename[0]))
            if len(newFile) > 0 and (newFile.__contains__("jpg") or newFile.__contains__("jpeg") or newFile.__contains__("png")):
                self.img.source = newFile
                # print(self.img.source)
            # self.img.reload()
        self.dismiss_popup()


class Editor(App):
    pass


# Factory.register('RootWidget', cls=RootWidget)
Factory.register('LoadDialog', cls=LoadDialog)
# Factory.register('SaveDialog', cls=SaveDialog)
# Factory.register('Picture', cls=SaveDialog)

if __name__ == '__main__':
    Editor().run()
