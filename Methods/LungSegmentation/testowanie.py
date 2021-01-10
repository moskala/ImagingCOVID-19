from MethodWatershed import SegmentationA
from MethodBinary import SegmentationB
import matplotlib.pyplot as plt

path = r"D:\Ala\covid\test\test"
# path = r"D:\Ala\covid\italy"
# path = r"D:\Studia\sem7\inzynierka\data\covidctscans_org\13_Italy\Original Dicom"

slices = SegmentationA.load_scan(path)
arr = SegmentationA.get_pixels_hu(slices)
test_segmented, test_lungfilter, test_outline, test_watershed, test_sobel_gradient, test_marker_internal, \
    test_marker_external, test_marker_watershed = SegmentationA.seperate_lungs(arr[2])

plt.imshow(test_segmented, cmap='gray')
plt.show()


ct_scan = SegmentationB.read_ct_scan(path)
segmented_ct_scan = SegmentationB.segment_lung_from_ct_scan(ct_scan,4)
        # sgmB.plot_ct_scan(segmented_ct_scan,self.plot.val)
        # test = sgmB.get_segmented_lungs(self.img.getdata())
        # plt.imshow(segmented_ct_scan,cmap='gray')
plt.imshow(segmented_ct_scan, cmap='gray')
plt.show()


