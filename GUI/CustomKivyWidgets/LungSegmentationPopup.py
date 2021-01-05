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

import random

class LungSegmentationPopup(Popup):

    def __init__(self,image_object):
        super().__init__()
        self.image_object = image_object
        plt.clf()
        print(self.image_object.file_type)
        if(self.image_object.file_type.__str__()=="DCM"):
            #if dicom, we run all 4 segmentation methods
            fig, ax = plt.subplots(2, 2)
            plt.axis('off')
            ax[0,0].imshow(self.image_object.get_current_slice(),cmap='gray')
            ax[0,1].imshow(self.image_object.get_segmented_lungs(),cmap='gray')
            ax[1,1].imshow(self.image_object.get_segmented_lungs_binary(),cmap='gray')
            bl = BoxLayout(orientation='horizontal')
            bl.add_widget(ResultFigure(fig=fig))
            self.box_layout.add_widget(bl,index=1)
        else:
            #only kmeans
            fig, (ax0, ax1) = plt.subplots(1, 2)
            ax0.imshow(self.image_object.get_current_slice(),cmap='gray')
            ax1.imshow(self.image_object.get_segmented_lungs(),cmap='gray')
            ax0.axis('off')
            ax1.axis('off')
            ax0.set_title('Original image')
            ax1.set_title('KMeans segmentation')
            filename = "temp_mask.jpg"
            fig.savefig(filename)
            bl = BoxLayout(orientation='horizontal')
            image = Image(source=filename)
            bl.add_widget(image)
            self.box_layout.add_widget(bl, index=1)
            bl_labels = BoxLayout(orientation='horizontal',size_hint_max_y=50)
            bl_labels.add_widget(Label(text='Original image'))
            bl_labels.add_widget(Label(text='KMeans segmentation'))
            self.box_layout.add_widget(bl_labels, index=1)
            image.reload()