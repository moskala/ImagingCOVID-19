
class Result():
    result = None
    lung_image = None
    scale = None
    image_width = None
    image_height = None
    file_name = None
    layer_number = None
    def __init__(self,result,lung_image,image_height,image_width,scale,file_name,layer_number):
        self.result = result
        self.lung_image = lung_image
        self.scale = scale
        self.image_height = image_height
        self.image_width = image_width
        self.file_name = file_name
        self.layer_number = layer_number

    def get_object_properties_headers(self):
        res = []
        res.append('Layer no')
        res.append('File name')
        res.append('Image size')
        res.append('Result')
        return res

    def get_object_properties_list(self):
        res = []
        res.append(self.layer_number)
        res.append(self.file_name)
        res.append(self.lung_image)
        res.append(str(self.image_height)+"x"+str(self.image_width))
        res.append(self.result)
        return res

    def get_object_ct_window(self):
        return self.scale

    def get_classifier(self):
        return ""

    def to_csv(self):
        pass

    def to_pdf(self):
        pass

    def get_method_name(self):
        pass


class AlexnetResult(Result):
    def __init__(self,result,lung_image,image_height,image_width,scale,file_name,layer_number,classifier):
        super().__init__(result,lung_image,image_height,image_width,scale,file_name,layer_number)
        self.classifier = classifier

    def get_classifier(self):
        return type(self.classifier).__name__

    def get_method_name(self):
        return 'Alex'

class HaralickGlcmResult(Result):
    def __init__(self,result,lung_image,image_height,image_width,scale,file_name,layer_number,classifier):
        super().__init__(result,lung_image,image_height,image_width,scale,file_name,layer_number)
        self.classifier = classifier

    def get_classifier(self):
        return type(self.classifier).__name__

    def get_method_name(self):
        return 'Haralick+GLCM'

class NeuralNetworkResult(Result):
    def __init__(self,result,lung_image,image_height,image_width,scale,file_name,layer_number):
        super().__init__(result,lung_image,image_height,image_width,scale,file_name,layer_number)

    def get_method_name(self):
        return 'Neural network for jpg/png'