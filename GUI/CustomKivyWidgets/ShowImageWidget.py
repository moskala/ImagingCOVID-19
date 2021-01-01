import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import sys
from pathlib import Path
sys.path.append(str(Path().resolve().parent / "Methods"))
import PlotUtilities as show


class MyFigure(FigureCanvasKivyAgg):
    """This class is used to display an image in GUI"""
    def __init__(self, val=0, image_data=None, **kwargs):
        """constructor"""
        if image_data is None:
            image_data = show.get_plot_data_jpg_png('../sample_image.jpg')
        plt.axis('off')
        plt.imshow(image_data, cmap='gray')
        super(MyFigure, self).__init__(plt.gcf(), **kwargs)
        self.curPlt = plt.gcf()
        self.image_data = image_data
        self.val = val
