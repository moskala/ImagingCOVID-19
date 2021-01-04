# Kivy imports
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.uix.image import Image as UixImage
from kivy.uix.popup import Popup


# Python imports
from pathlib import Path
import sys
from PIL import Image as PilImage

# Implemented methods imports
sys.path.append(str(Path().resolve().parent / "Methods"))
from Grayscale import *


class DrawPopup(Popup):

    def __init__(self):
        super().__init__()


class DrawFigure(UixImage):

    marked_regions = None
    current_marked_points = None
    temp_filename = 'temp.jpg'

    def __init__(self, image_data, **kwargs):
        image = PilImage.fromarray(convert_array_to_grayscale(image_data))
        self.img_width = image_data.shape[1]
        self.img_height = image_data.shape[0]
        image.save(self.temp_filename)
        super().__init__(source=self.temp_filename, **kwargs)
        self.id = "draw_figure"
        self.allow_stretch = True
        self.marked_regions = []
        self.current_marked_points = []
        self.canvas.after.clear()
        self.reload()
        self.rect = None
        self.draw_warning_rectangle()
        self.bind(pos=self.update_size,
                  size=self.update_size)

    def get_image_position(self):
        curr_img_width, curr_img_height = self.calculate_image_size(self.size)
        margin_horizontal, margin_vertical = self.calculate_margins(curr_img_width, curr_img_height)
        x0 = self.pos[0] + margin_horizontal
        y0 = self.pos[1] + margin_vertical
        return x0, y0

    def calculate_margins(self, image_width, image_height):

        margin_horizontal = (self.size[0] - image_width) / 2
        margin_vertical = (self.size[1] - image_height) / 2
        return margin_horizontal, margin_vertical

    def calculate_image_size(self, size):

        if self.image_ratio >= 1:
            curr_img_width = size[0]
            curr_img_height = curr_img_width / self.image_ratio
            if curr_img_height > size[1]:
                curr_img_height = size[1]
                curr_img_width = curr_img_height * self.image_ratio
        else:
            curr_img_height = size[1]
            curr_img_width = curr_img_height * self.image_ratio
            if curr_img_width > size[0]:
                curr_img_width = size[0]
                curr_img_height = curr_img_width / self.image_ratio

        return curr_img_width, curr_img_height

    def update_size(self, *args):
        self.redraw_regions(self.size, self.pos)

    def on_touch_down(self, touch):

        curr_img_width, curr_img_height = self.calculate_image_size(self.size)

        ratio_horizontal = curr_img_width / self.img_width
        ratio_vertical = curr_img_height / self.img_height
        x0, y0 = self.get_image_position()

        x = (touch.x - x0) / ratio_vertical
        y = (touch.y - y0) / ratio_horizontal

        if 0 <= x and x <= self.img_width and y >=0 and y <= self.img_height:
            self.current_marked_points.append((x, y))
            with self.canvas.after:
                Color(1, 0, 0)
                d = 5.
                Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))

        return super(DrawFigure, self).on_touch_down(touch)

    def add_new_region(self, *args):
        if len(self.current_marked_points) > 2:
            self.marked_regions.append(list(self.current_marked_points))
            self.current_marked_points = []
            self.redraw_regions()

    def delete_current_region(self, *args):
        if self.current_marked_points:
            self.current_marked_points = []
        else:
            self.marked_regions = self.marked_regions[0:-1]
        self.redraw_regions()

    def calculate_coefficients(self, size, pos):
        curr_img_width, curr_img_height = self.calculate_image_size(size)
        margin_horizontal, margin_vertical = self.calculate_margins(curr_img_width, curr_img_height)

        ratio_horizontal = curr_img_width / self.img_width
        ratio_vertical = curr_img_height / self.img_height
        ax = ratio_horizontal
        bx = pos[0] + margin_horizontal
        ay = ratio_vertical
        by = pos[1] + margin_vertical
        return ax, bx, ay, by

    def redraw_regions(self, size=None, pos=None):

        if size is None:
            size = self.size
            pos = self.pos
        ax, bx, ay, by = self.calculate_coefficients(size, pos)

        self.canvas.after.clear()
        self.update_rect()

        with self.canvas.after:
            for region in self.marked_regions:
                new_points = [(x * ax + bx,
                               y * ay + by)
                              for x, y in region]
                for x1, y1 in new_points:
                    Color(1, 1, 0, 1)
                    d = 5.
                    Ellipse(pos=(x1 - d / 2, y1 - d / 2), size=(d, d))

                points_flatten = list(sum(new_points, ()))
                Line(points=points_flatten, width=1, close=True)

    def get_regions(self):
        return self.marked_regions

    def finish_drawing(self, *args):
        if len(self.current_marked_points) > 2:
            self.add_new_region()
            self.add_new_region()
        Path(self.temp_filename).unlink()
        return self.marked_regions

    def draw_warning_rectangle(self):

        x, y = self.get_image_position()
        w, h = self.calculate_image_size(self.size)

        with self.canvas.before:
            Color(1, 0, 0, 0.5)
            self.rect = Rectangle(size=(w, h),
                                  pos=(x, y))

    def update_rect(self):

        x, y = self.get_image_position()
        w, h = self.calculate_image_size(self.size)
        self.rect.pos = (x, y)
        self.rect.size = (w, h)

