from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from pathlib import Path
import matplotlib.pyplot as plt
import logging
import sys
import os

# Custom kivy widgets imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from ErrorPopup import ErrorPopup


class LungSegmentationPopup(Popup):

    source_file = None
    _error_popup = None

    def __init__(self, image_object):
        super().__init__()
        self.image_object = image_object
        plt.clf()
        filename = self.image_object.get_segmentation_figure()
        bl = BoxLayout(orientation='horizontal')
        image = Image(source=filename)
        bl.add_widget(image)
        self.box_layout.add_widget(bl, index=1)
        image.reload()
        self.source_file = filename
        self.bind(on_dismiss=self.delete_file)

    def delete_file(self, *args):
        try:
            Path(self.source_file).unlink()
        except Exception as error:
            logging.error(": " + str(error))
            self._error_popup = ErrorPopup(message=str(error))
