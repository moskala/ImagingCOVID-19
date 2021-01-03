from LungSegmentation.LungSegmentation_MethodKMeans_AllTypes import *
from ImageClass import *

import gc


class ChooseSlices:
    @staticmethod
    def choose(image_object, fraction=0.2):
        # sys.stdout = open("test.txt", "w")
        print('Processing...')
        al = []
        indexes = []
        one3 = int(image_object.total_slice_number/3)
        print('one3',one3)
        two3 = int(one3*2)
        for i in range(one3,two3,3):
            try:
                img = image_object.get_next_slice(i)
                al.append(make_lungmask(img))
                print(i)
                indexes.append(i)
            except Exception as ex:
                print(str(ex))
                print(i)
                if(ex.args.__contains__('min() arg is an empty sequence')):
                    continue
                else:
                    break
        # quo = []
        # gc.disable()
        # for slc in al:
        #     flat_list = [item for sublist in slc for item in sublist]
        #     non_zeros = [element for element in flat_list if element > 0]
        #     quo.append(len(non_zeros) / len(flat_list))
        # gc.enable()
        # quo.sort(reverse=True)
        # #ind = [quo.index(num) for num in quo if round(num, 1) == threshold]
        # return [quo.index(num) for num in quo[0:round(fraction*len(quo))]]

        ##wersja ze slownikiem
        # quo={}
        # gc.disable()
        # it=0
        # for slc in al:
        #     flat_list = [item for sublist in slc for item in sublist]
        #     non_zeros = [element for element in flat_list if element > 0]
        #     quo.update({it: len(non_zeros) / len(flat_list)})
        #     it=it+1
        # gc.enable()
        # #quo = dict(sorted(quo.items(), key=lambda item: item[1],reverse=True))
        # srtd = dict(sorted(quo.items(), key=lambda item: item[1],reverse=True))
        return al,indexes
        # print(quo)
        # print(len(numpy.array(al[40])))
        # print(len(al))

#numpy.set_printoptions(threshold=sys.maxsize)
