from LungSegmentation_MethodB_dicom import SegmentationB

from pathlib import Path,PurePath
import os,sys
import dicom
import numpy
import gc

class ChooseSlices:
    @staticmethod
    def choose(path,threshold):
        # sys.stdout = open("test.txt", "w")
        print('Processing...')
        sgm = SegmentationB()
        ct_scan = sgm.read_ct_scan(path)
        al = sgm.segment_lung_from_ct_scan_all(ct_scan)
        quo=[]
        gc.disable()
        for slc in al:
            flat_list = [item for sublist in slc for item in sublist]
            nonZeros = [element for element in flat_list if element > 0]
            quo.append(len(nonZeros)/len(flat_list))
        gc.enable()
        ind=[quo.index(num) for num in quo if round(num,1)==threshold]
        return ind
        # print(quo)
        # print(len(numpy.array(al[40])))
        # print(len(al))

#numpy.set_printoptions(threshold=sys.maxsize)
