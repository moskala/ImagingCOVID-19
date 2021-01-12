import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ImageMedical.ImageClass import JpgImage, PngImage
import LungSegmentation.LungSegmentationUtilities as sgUtils
import LungSegmentation.MethodUNetXRay as sgUnet


class XRayJpgImage(JpgImage):
    """
    Class for representing jpg image object.
    """

    def __init__(self, folder, filename):
        super().__init__(folder, filename)

    def get_segmented_lungs(self):
        segment, mask = sgUnet.make_lungmask(self.src_filename, self.src_folder)
        return segment

    def get_segmentation_figure(self):
        segment = self.get_segmented_lungs()
        figures = [self.get_current_slice(), segment]
        titles = ['Original image', 'X-Ray segmentation']

        filename = sgUtils.get_segmentation_figure(figures, titles)

        return filename


class XRayPngImage(PngImage):
    """
    Class for representing png image object.
    """

    def __init__(self, folder, filename):
        super().__init__(folder, filename)

    def get_segmented_lungs(self):
        segment, mask = sgUnet.make_lungmask(self.src_filename, self.src_folder)
        return segment

    def get_segmentation_figure(self):
        segment = self.get_segmented_lungs()
        figures = [self.get_current_slice(), segment]
        titles = ['Original image', 'X-Ray segmentation']

        filename = sgUtils.get_segmentation_figure(figures, titles)

        return filename
