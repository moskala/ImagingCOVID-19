from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from pathlib import Path
import matplotlib.pyplot as plt


class LungSegmentationPopup(Popup):

    source_file = None

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
        image.reload()
        self.source_file = filename
        self.bind(on_dismiss=self.delete_file)

    def delete_file(self, *args):
        Path(self.source_file).unlink()


