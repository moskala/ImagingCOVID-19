

class Result:
    result = None
    lung_image = None
    scale = None
    image_width = None
    image_height = None
    file_name = None
    layer_number = None

    def __init__(self, result, lung_image, image_height, image_width, scale, file_name, layer_number, examination_type):
        self.result = result
        self.lung_image = lung_image
        self.scale = scale
        self.image_height = image_height
        self.image_width = image_width
        self.file_name = file_name
        self.layer_number = layer_number
        self.examination_type = examination_type

    def get_object_properties_headers(self):
        res = ['Layer no', 'File name', 'Image size', 'Result']
        return res

    def get_object_properties_list(self):
        res = [self.layer_number, self.file_name, self.lung_image, str(self.image_height) + "x" + str(self.image_width),
               self.result]
        return res

    def get_object_properties_list_without_image(self):
        res = [self.layer_number, self.file_name, str(self.image_height) + "x" + str(self.image_width), self.result]
        return res

    def get_object_ct_window(self):
        return self.scale

    def get_classifier(self):
        return ""

    def get_examination_type(self):
        return self.examination_type

    def get_method_name(self):
        pass


class AlexnetResult(Result):
    def __init__(self, result, lung_image, image_height, image_width, scale, file_name, layer_number, examination_type, classifier):
        super().__init__(result, lung_image, image_height, image_width, scale, file_name, layer_number, examination_type)
        self.classifier = classifier

    def get_classifier(self):
        return type(self.classifier).__name__

    def get_method_name(self):
        return 'Alex'


class HaralickGlcmResult(Result):
    def __init__(self, result, lung_image, image_height, image_width, scale, file_name, layer_number, examination_type, classifier):
        super().__init__(result, lung_image, image_height, image_width, scale, file_name, layer_number, examination_type)
        self.classifier = classifier

    def get_classifier(self):
        return type(self.classifier).__name__

    def get_method_name(self):
        return 'Haralick+GLCM'


class NeuralNetworkResult(Result):
    def __init__(self, result, lung_image, image_height, image_width, scale, file_name, layer_number, examination_type):
        super().__init__(result, lung_image, image_height, image_width, scale, file_name, layer_number, examination_type)

    def get_method_name(self):
        return 'Neural network for jpg/png'


class SeverityResult(Result):

    severity = None
    percentage = None

    def __init__(self, result, slice, image_properties, layer_number, examination_type):
        super().__init__(result,
                         lung_image=slice,
                         image_height=image_properties["Height"],
                         image_width=image_properties["Width"],
                         scale=image_properties["CT Window Type"],
                         file_name=image_properties["Filename"],
                         layer_number=layer_number,
                         examination_type=examination_type)

        self.percentage = result[0]
        self.severity = result[1]

    def get_method_name(self):
        return 'Severity score'

    def get_object_properties_list(self):
        res = [self.layer_number,
               self.file_name,
               self.lung_image,
               str(self.image_height) + "x" + str(self.image_width),
               str("{:.2f}%, severity: {}".format(self.percentage, self.severity)),
               ]
        return res
