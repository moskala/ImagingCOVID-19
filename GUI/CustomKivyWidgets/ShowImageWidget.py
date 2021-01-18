# Kivy imports
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

# Python imports
import matplotlib.pyplot as plt
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Methods')))
from PlotUtilities import get_plot_data_jpg_png


START_IMAGE = "sample_image.jpg"


class MyFigure(FigureCanvasKivyAgg):
    """This class is used to display an image in GUI"""
    def __init__(self, val=0, image_data=None, **kwargs):
        """constructor"""
        if image_data is None:
            image_data = get_plot_data_jpg_png(START_IMAGE)
        plt.clf()   # very important to clear plt before new figure
        plt.axis('off')
        plt.imshow(image_data, cmap='gray')
        super(MyFigure, self).__init__(plt.gcf(), **kwargs)
        self.curPlt = plt.gcf()
        self.image_data = image_data
        self.val = val


class ResultFigure(FigureCanvasKivyAgg):

    def __init__(self, fig=None, **kwargs):
        """constructor"""
        if fig is not None:
            plt.clf()   # very important to clear plt before new figure
            super(ResultFigure, self).__init__(fig, **kwargs)
            self.curPlt = fig
        else:
            logging.error("Segmentation figure: fig is None")
