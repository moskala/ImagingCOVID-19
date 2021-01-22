from pathlib import Path
import matplotlib.pyplot as plt

from TestsContext import Methods
from Methods.LungSegmentation.MethodWatershed import SegmentationA, seperate_lungs_and_mask, generate_markers
from Methods.LungSegmentation.MethodBinary import SegmentationB
from Methods.LungSegmentation.MethodKMeans import make_lungmask_oryginal
from Methods.LungSegmentation.MethodUNetXRay import make_lungmask
from Methods.ImageMedical.CTImageClass import CTDicomImage
from Methods.ImageMedical.XRayImageClass import XRayJpgImage


testDir = 'test_data/testcase_dicom_hu'
testFile = 'testcase_hounsfield1.dcm'


def test_markers(folder, file):
    img = CTDicomImage(folder, file)
    marker_internal, marker_external, marker_watershed = generate_markers(img.get_current_slice())
    plt.imshow(marker_watershed, cmap='gray')
    plt.axis('off')
    plt.show()


def show_segmentation(folder, file):
    img = CTDicomImage(folder, file)
    lungs, mask = seperate_lungs_and_mask(img.get_current_slice())
    plt.imshow(lungs, cmap='gray')
    plt.axis('off')
    plt.show()


def show_original_image(folder, file):
    img = CTDicomImage(folder, file)
    plt.imshow(img.get_current_slice(), cmap='gray')
    plt.axis('off')
    plt.show()


def show_binary(folder, file):
    img = CTDicomImage(folder, file)
    image = img.get_current_slice()
    lungs = SegmentationB.get_segmented_lungs(image.copy(), -400)
    plt.imshow(image, cmap='gray')
    plt.axis('off')
    plt.show()
    plt.imshow(lungs, cmap='gray')
    plt.axis('off')
    plt.show()


def show_kmeans(folder, file):
    img = CTDicomImage(folder, file)
    image = img.get_current_slice()
    lungs = make_lungmask_oryginal(image.copy())
    plt.imshow(image, cmap='gray')
    plt.axis('off')
    plt.show()
    plt.imshow(lungs, cmap='gray')
    plt.axis('off')
    plt.show()


def check_size(folder, file):
    im = CTDicomImage(folder, file)
    print(im.get_image_size())


def show_xray(folder, file):

    img = XRayJpgImage(folder, file)
    image = img.get_current_slice()
    print(img.get_image_size())
    lungs, mask = make_lungmask(file, folder)
    plt.imshow(image, cmap='gray')
    plt.axis('off')
    plt.show()
    plt.imshow(lungs, cmap='gray')
    plt.axis('off')
    plt.show()


def show_all():
    # Print image size
    check_size(Path(testDir).resolve(), testFile)

    # Show original image
    show_original_image(Path(testDir).resolve(), testFile)

    # Show markers watershed
    test_markers(Path(testDir).resolve(), testFile)

    # Show segmentation watershed
    show_segmentation(Path(testDir).resolve(), testFile)

    # Show segmentation binary
    show_binary(Path(testDir).resolve(), testFile)

    # Show segmentation kmeans
    show_kmeans(Path(testDir).resolve(), testFile)

    show_xray(Path("test_Data").resolve() / "testcase_xray", "xray.jpeg")


if __name__ == "__main__":
    show_all()
