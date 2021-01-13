from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty

import os


class LoadDialog(FloatLayout):
    """This class is used to run the load dialog"""
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    """This class is used to run the save dialog"""
    save = ObjectProperty(None)
    img = ObjectProperty(None)
    cancel = ObjectProperty(None)

