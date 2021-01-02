# Kivy imports
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.uix.image import Image as UixImage
from kivy.core.image import Image as CoreImage

# Python imports
from pathlib import Path
import sys
from PIL import Image as PilImage

# Implemented methods imports
sys.path.append(str(Path().resolve().parent / "Methods"))
from Grayscale import *


class MyDrawFigure(UixImage):

    marked_regions = []
    current_marked_points = []

    def __init__(self, image_data=None, **kwargs):

        image = PilImage.fromarray(convert_array_to_grayscale(image_data))
        self.img_width = image_data.shape[1]
        self.img_height = image_data.shape[0]
        image.save('temp.jpg')
        super().__init__(source='temp.jpg', **kwargs)
        self.id = "draw_figure"
        self.allow_stretch = True
        self.draw_rectangle()

    def get_image_position(self, size):
        curr_img_width, curr_img_height = self.calculate_image_size(size)
        margin_horizontal, margin_vertical = self.calculate_margins(size, curr_img_width, curr_img_height)
        x0 = self.pos[0] + margin_horizontal
        y0 = self.pos[1] + margin_vertical
        return x0, y0

    def calculate_image_size(self, size):
        border = min(size)
        if size[0] < size[1]:
            ratio = border / self.img_width
        else:
            ratio = border / self.img_height

        curr_img_width = ratio * self.img_width
        curr_img_height = ratio * self.img_height

        return curr_img_width, curr_img_height

    def calculate_margins(self, size, image_width, image_height):

        margin_horizontal = (size[0] - image_width) / 2
        margin_vertical = (size[1] - image_height) / 2
        # margin_horizontal = max(margin_horizontal, 0) # TODO dlaczego są ujemne czasem?
        # margin_vertical = max(margin_vertical, 0)
        return margin_horizontal, margin_vertical

    def update_size(self, instance, new_size):
        # print("self", self.size)
        # print("inst", instance.size)
        # print("new", new_size)
        # print("pos", instance.pos)
        diff = np.subtract(new_size, self.size)

        if not np.any(diff):
            return
        # print("difference", diff)
        self.redraw_regions(new_size, self.pos)

    def on_touch_down(self, touch):
        # print('self id', self.id)
        # print('self size ', self.size)
        # print('self pos ', self.pos)
        # print('touch ', touch.x, touch.y)
        # print('window', Window.size)
        # print('hint', self.pos_hint)

        curr_img_width, curr_img_height = self.calculate_image_size(self.size)

        ratio_horizontal = curr_img_width / self.img_width
        ratio_vertical = curr_img_height / self.img_height
        x0, y0 = self.get_image_position(self.size)

        x = (touch.x - x0) / ratio_vertical
        y = (touch.y - y0) / ratio_horizontal
        # print("x, y", x, y)

        if 0 <= x and x <= self.img_width and y >=0 and y <= self.img_height:
            self.current_marked_points.append((x, y))
            with self.canvas.after:
                Color(1, 0, 0)
                d = 5.
                Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))

        return super(MyDrawFigure, self).on_touch_down(touch)

    def add_new_region(self, *args):
        self.marked_regions.append(list(self.current_marked_points))
        self.current_marked_points = []
        self.redraw_regions()

    def delete_current_region(self, *args):
        self.current_marked_points = []
        self.redraw_regions()

    def calculate_coefficients(self, size, pos):
        curr_img_width, curr_img_height = self.calculate_image_size(size)
        margin_horizontal, margin_vertical = self.calculate_margins(size, curr_img_width, curr_img_height)

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
        self.update_rect(size)

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

    def finish_drawing(self):
        if self.current_marked_points:
            self.add_new_region()

    # TODO wykorzystać lub usunąć
    def draw_mask(self, mask):
        image = PilImage.fromarray(convert_array_to_grayscale(mask))
        image.save('temp_mask.jpg')
        texture = CoreImage('temp_mask.jpg').texture

        x, y = self.get_image_position(self.size)
        w, h = self.calculate_image_size(self.size)

        with self.canvas.before:
            Color(1, 0, 0, 0.5)  # green; colors range from 0-1 instead of 0-255
            self.rect = Rectangle(texture=texture,
                                  size=(w, h),
                                  pos=(x, y))

    def draw_rectangle(self):

        x, y = self.get_image_position(self.size)
        w, h = self.calculate_image_size(self.size)

        with self.canvas.before:
            Color(1, 0, 0, 0.5)  # green; colors range from 0-1 instead of 0-255
            self.rect = Rectangle(size=(w, h),
                                  pos=(x, y))

    def update_rect(self, size):

        x, y = self.get_image_position(size)
        w, h = self.calculate_image_size(size)
        self.rect.pos = (x, y)
        self.rect.size = (w, h)


# TODO wykorzystac lub usunac
class MyImage(UixImage):

    draw_points = None
    img_width = None
    img_height = None

    def __init__(self, image_data, **kwargs):
        image = PilImage.fromarray(convert_array_to_grayscale(image_data))
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
            Color(1, 1, 0, 1)
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
