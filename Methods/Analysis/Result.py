
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

    def get_object_properties(self):
        return self.file_name,self.lung_image,self.image_height,self.image_width,self.scale,self.result

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