from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty

import os


class LoadDialog(FloatLayout):
    """This class is used to run the load dialog"""
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("hello")
        self.ids.filechooser.path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'images_data'))


class SaveDialog(FloatLayout):
    """This class is used to run the save dialog"""
    save = ObjectProperty(None)
    img = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def __init__(self, **kwargs):
        # print(**kwargs)
        super(SaveDialog, self).__init__()

        self.ids.filechooser.path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'images_data'))
        print("hello2")


class MySaveDialog(FloatLayout):
    """This class is used to run the save dialog"""
    save = ObjectProperty(None)
    img = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def __init__(self, **kwargs):
        # print(**kwargs)
        super(MySaveDialog, self).__init__()

        self.ids.filechooser_save.path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'images_data'))
        print("hello2")

