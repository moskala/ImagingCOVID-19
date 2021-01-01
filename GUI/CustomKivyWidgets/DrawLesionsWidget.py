import matplotlib
# matplotlib.use('Agg', force=True)  # comment this line to see effect
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse,Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.core.image import Image as CoreImage
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image as UixImage
from kivy.uix.slider import Slider
from kivy.graphics.texture import Texture
from kivy.core.window import Window
import pydicom
from pathlib import Path
import sys
from PIL import Image as PilImage
import csv
import os, time
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
# matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
sys.path.append(str(Path().resolve().parent / "Methods"))
from Grayscale import *



class MyDrawFigure(FigureCanvasKivyAgg):

    def __init__(self, image_data=None, **kwargs):
        plt.axis('off')
        plt.imshow(image_data, cmap='gray')
        super().__init__(plt.gcf(), **kwargs)
        self.img_width = image_data.shape[1]
        self.img_height = image_data.shape[0]
        self.id = "hello"
        self.padding = 0, 0, 0, 0
        self.margin = 0, 0, 0, 0
        # self.pos = self.setter('pos')

    def set_canvas(self):
        with self.canvas.after:
            Color(0, 1, 0, 1)  # blue; colors range from 0-1 not 0-255
            Rectangle(size=self.size, pos=self.pos)



# class MyPaintWidget(Widget):
#     def on_touch_down(self, touch):
#         with self.canvas:
#             Color(1, 1, 0)
#             d = 30.
#             Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))






# class MyPaintFigure(MyFigure):
#
#     draw_points = None
#
#     def __init__(self, image_data, **kwargs):
#         super().__init__(image_data=image_data)
#         self.draw_points = []
#
#     def on_touch_down(self, touch):
#         with self.canvas:
#             Color(1, 1, 0)
#             touch.apply_transform_2d(self.to_widget)
#             d = 5.
#             Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
#             print((touch.x-self.pos[0], touch.y-self.pos[1]))
#             print(self.draw_points)
#
#     def get_points(self):
#         return self.draw_points


class MyImage(UixImage):

    draw_points = None
    img_width = None
    img_height = None

    def __init__(self, image_data, **kwargs):
        image = Image.fromarray(convert_array_to_grayscale(image_data))
        image.save('test.jpg')
        super().__init__(source='test.jpg')
        self.draw_points = []
        self.img_width = image.width
        self.img_height = image.height
        #os.remove('test.jpg')

    def on_touch_down(self, touch):
        new_img_width = self.size[1]*self.img_width / self.img_height
        margin = (self.size[0]-new_img_width) / 2 + self.pos[0]
        print('margin ', margin)
        with self.canvas:
            Color(1, 1, 0)
            print('self ', self)
            print('self size ', self.size)
            print('self pos ', self.pos)
            print('touch ', touch.x-margin, touch.y-self.pos[1])
            d = 5.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            if touch.y - self.pos[1] < self.size[1]:
                self.draw_points.append((int(touch.x-margin), int(touch.y-self.pos[1])))

    def get_points(self):
        return self.draw_points

from functools import partial
from random import random as r

class MyImageAla(BoxLayout):

    draw_points = None
    img_width = None
    img_height = None
    image = None

    def add_rects(self, label, wid, count, *largs):
        label.text = str(int(label.text) + count)
        with wid.canvas:
            for x in range(count):
                Color(r(), 1, 1, mode='hsv')
                Rectangle(pos=(r() * wid.width + wid.x,
                               r() * wid.height + wid.y), size=(20, 20))

    def double_rects(self, label, wid, *largs):
        count = int(label.text)
        self.add_rects(label, wid, count, *largs)

    def reset_rects(self, label, wid, *largs):
        label.text = '0'
        wid.canvas.clear()

    def __init__(self):
        super().__init__(orientation='vertical')
        wid = Widget()

        label = Label(text='0')

        btn_add100 = Button(text='+ 100 rects',
                            on_press=partial(self.add_rects, label, wid, 100))

        btn_add500 = Button(text='+ 500 rects',
                            on_press=partial(self.add_rects, label, wid, 500))

        btn_double = Button(text='x 2',
                            on_press=partial(self.double_rects, label, wid))

        btn_reset = Button(text='Reset',
                           on_press=partial(self.reset_rects, label, wid))

        layout = BoxLayout(size_hint=(1, None), height=50)
        layout.add_widget(btn_add100)
        layout.add_widget(btn_add500)
        layout.add_widget(btn_double)
        layout.add_widget(btn_reset)
        layout.add_widget(label)

        # box = BoxLayout(orientation='vertical')
        self.add_widget(wid)
        self.add_widget(layout)

        # return box

    #
    # def __init__(self, image_object: ImageObject, **kwargs):
    #     super().__init__()
    #     self.draw_points = []
    #     w, h = image_object.get_size()
    #     self.img_width = w
    #     self.img_height = h
    #     print(w)
    #     print(h)
    #     # os.remove('test.jpg')
    #     self.image = convert_array_to_grayscale(image_object.pixel_array)
    #     # texture = Texture.create(size=(w, h))
    #     # texture.blit_buffer(img.flatten(), colorfmt='rgb', bufferfmt='ubyte')
    #     # w_img = Image(size=(w, h), texture=texture)
    #     print(self.pos)
    #     print(Window.size)
    #
    #     # with self.canvas:
    #     #     Rectangle(texture=texture, pos=self.pos, size=self.size)
    #
    # def _update_rect(self, instance, value):
    #     self.rect.pos = instance.pos
    #     self.rect.size = instance.size
    #
    # def load_image_on_canvas(self):
    #     print(self.size)
    #     # with self.canvas.before:
    #     #     Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
    #     #     self.rect = Rectangle(size=(self.img_width, self.img_height), pos=self.parent.pos)
    #
    #     # self.bind(size=self._update_rect, pos=self._update_rect)
    #     # texture = Texture.create(size=(self.img_width, self.img_height))
    #     # texture.blit_buffer(self.image.flatten(), colorfmt='rgb', bufferfmt='ubyte')
    #     # print("Texture created")
    #     print(self.parent.pos)
    #     print(self.parent.size)
    #     with self.canvas:
    #         # Rectangle(texture=texture, pos=self.pos, size=self.size)
    #         Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
    #         self.rect = Rectangle(size=(100, 100), pos=self.parent.pos)
    #
    #     print(type(self.parent))
    #     # print(self.parent.id)

    # def on_touch_down(self, touch):
    #     new_img_width = self.size[1] * self.img_width / self.img_height
    #     margin = (self.size[0] - new_img_width) / 2 + self.pos[0]
    #     print('margin ', margin)
    #     with self.canvas:
    #         Color(1, 1, 0)
    #         print('self ', self)
    #         print('self size ', self.size)
    #         print('self pos ', self.pos)
    #         print('touch ', touch.x - margin, touch.y - self.pos[1])
    #         d = 5.
    #         Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
    #         if touch.y - self.pos[1] < self.size[1]:
    #             self.draw_points.append((int(touch.x - margin), int(touch.y - self.pos[1])))


