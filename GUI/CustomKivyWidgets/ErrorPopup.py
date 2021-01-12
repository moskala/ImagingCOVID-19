# Kivy imports
from kivy.uix.popup import Popup
from kivy.uix.label import Label


class ErrorPopup(Popup):

    def __init__(self, message=""):
        super().__init__()
        self.title = "Error occurrence"
        self.auto_dismiss = True
        msg = '[color=ff0000]''Error occurred!\n{}''[/color]'.format(message)
        self.content.text = msg

        self.open()
