
class Result():
    result = None
    lung_image = None
    scale = None
    image_width = None
    image_height = None
    file_name = None
    def __init__(self,result,lung_image,image_height,image_width,scale,file_name):
        self.result = result
        self.lung_image = lung_image
        self.scale = scale
        self.image_height = image_height
        self.image_width = image_width
        self.file_name = file_name

    def get_object_properties_headers(self):
        res = []
        res.append('No')
        res.append('File name')
        res.append('Image size')
        res.append('Result')
        return res

    def get_object_properties_list(self):
        res = []
        res.append(self.file_name)
        res.append(self.lung_image)
        res.append(str(self.image_height)+"x"+str(self.image_width))
        res.append(self.result)
        return res

    def get_object_ct_window(self):
        return self.scale


    def to_csv(self):
        pass

    def to_pdf(self):
        pass

    def get_method_name(self):
        pass


class AlexnetResult(Result):
    def __init__(self,result,lung_image,image_height,image_width,scale,file_name):
        super().__init__(result,lung_image,image_height,image_width,scale,file_name)
    
    def get_method_name(self):
        return 'Alex'

class HaralickGlcmResult(Result):
    def __init__(self,result,lung_image,image_height,image_width,scale,file_name):
        super().__init__(result,lung_image,image_height,image_width,scale,file_name)
    
    def get_method_name(self):
        return 'Haralick+GLCM'