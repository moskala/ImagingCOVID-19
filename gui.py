from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.core.image import Image as CoreImage
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image

import os

class Picture(Scatter):
    '''Picture is the class that will show the image with a white border and a
    shadow. They are nothing here because almost everything is inside the
    picture.kv. Check the rule named <Picture> inside the file, and you'll see
    how the Picture() is really constructed and used.

    The source property will be the filename to show.
    '''



class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    img = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    image = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        # self.image = CoreImage(os.path.join(path, filename[0]))
        # try:
            # load the image
        picture = Image(source=os.path.join(path, filename[0]))
            # add to the main field
        # self.add_widget(picture)
        # except Exception as e:
           # Logger.exception('Pictures: Unable to load <%s>' % filename)
        self.img.source = os.path.join(path, filename[0])
        # self.img.reload()
        self.dismiss_popup()

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)

        self.dismiss_popup()


class Editor(App):
    pass


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
# Factory.register('SaveDialog', cls=SaveDialog)
# Factory.register('Picture', cls=SaveDialog)

if __name__ == '__main__':
    Editor().run()