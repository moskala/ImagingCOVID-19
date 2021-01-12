# Kivy imports
from kivy.uix.popup import Popup
from kivy.uix.label import Label


class ErrorPopup(Popup):

    def __init__(self, message=""):
        super().__init__()
        self.title = "Error popup"
        self.auto_dismiss = True
        self.size_hint = (.6, .6)
        msg = '[color=ff0000]''Error occurred!\n{}''[/color]'.format(message)
        self.content = Label(text=msg, markup=True)

        self.open()
