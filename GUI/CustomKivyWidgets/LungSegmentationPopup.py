from kivy.uix.popup import Popup
from CustomKivyWidgets.ShowImageWidget import ResultFigure
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
import sys
from kivy.uix.label import Label
from pathlib import Path
import matplotlib.pyplot as plt

sys.path.append(str(Path().resolve().parent.parent / "Methods"))
from ImageClass import ImageType



class LungSegmentationPopup(Popup):

    def __init__(self, image_object):
        super().__init__()
        self.image_object = image_object
        plt.clf()
        print(self.image_object.file_type)
        filename = self.image_object.get_segmentation_figure()
        bl = BoxLayout(orientation='horizontal')
        image = Image(source=filename)
        bl.add_widget(image)
        self.box_layout.add_widget(bl, index=1)
        # bl_labels = BoxLayout(orientation='horizontal', size_hint_max_y=50)
        # bl_labels.add_widget(Label(text='Original image'))
        # bl_labels.add_widget(Label(text='KMeans segmentation'))
        # self.box_layout.add_widget(bl_labels, index=1)
        image.reload()


