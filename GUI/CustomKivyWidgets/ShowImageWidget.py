# Kivy imports
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

# Python imports
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.append(str(Path().resolve().parent / "Methods"))
from PlotUtilities import get_plot_data_jpg_png


START_IMAGE = "sample_image.jpg"


class MyFigure(FigureCanvasKivyAgg):
    """This class is used to display an image in GUI"""
    def __init__(self, val=0, image_data=None, fig=None,**kwargs):
        """constructor"""
        if(fig is not None):
            super(MyFigure, self).__init__(fig, **kwargs)
            self.curPlt = fig
        else:
            if image_data is None:
                image_data = get_plot_data_jpg_png(START_IMAGE)
            else:
                plt.clf()
            plt.axis('off')
            plt.imshow(image_data, cmap='gray')
            super(MyFigure, self).__init__(plt.gcf(), **kwargs)
            self.curPlt = plt.gcf()
            self.image_data = image_data
            self.val = val
