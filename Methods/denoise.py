import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from skimage import img_as_float
from skimage.restoration import denoise_nl_means
from ImageClass import *

class Denoise:

    @staticmethod
    def ImageDenoise(image,h=0.01):
        """function denoises an image of type ImageObject"""
        res = denoise_nl_means(img_as_float(image.get_current_slice()),h=h)
        #res = denoise_nl_means(image.get_current_slice(),h=h)
        f, axarr = plt.subplots(1,2)
        axarr[0].imshow(image.get_current_slice(),cmap='gray')
        axarr[1].imshow(res,cmap='gray')
        plt.show()

#img = JpgImage(r"C:\Users\Maya\studia\4rok\inz\covidSeg\png",r"3.jpg")
#img = PngImage(r"C:\Users\Maya\studia\4rok\inz\ai\Contrastive-COVIDNet\data\COVID-CT\test",r"112.png")
img = DicomImage(r"C:\Users\Maya\studia\4rok\inz\covidSeg\wloch1",r"Italy_case010058.dcm")
#ten nie jest w rgb ani grayscale
#img = DicomImage(r"C:\Users\Maya\studia\4rok\inz\repo\ImagingCOVID-19\Methods\tests\test_data\79262",r"1-080.dcm")

Denoise.ImageDenoise(img,0.001)

# jak dobrac parametr h oraz czy uzywamy as float czy nie?


