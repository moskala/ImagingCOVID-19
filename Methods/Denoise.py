from matplotlib import pyplot as plt
from skimage import img_as_float
from skimage.restoration import denoise_nl_means
from ImageMedical.ImageClass import *

class Denoise:

    @staticmethod
    def ImageDenoise(image,h=0.01):
        """function denoises an image of type ImageObject"""
        res = denoise_nl_means(img_as_float(image.get_current_slice()),h=h)
        f, axarr = plt.subplots(1,2)
        axarr[0].imshow(image.get_current_slice(),cmap='gray')
        axarr[1].imshow(res,cmap='gray')
        plt.show()




