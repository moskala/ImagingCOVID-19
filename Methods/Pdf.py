""" this is the class containing the PDF creating methods """
from fpdf import FPDF


class PDF(FPDF):

    def set_font_characteristics(self, font_size, isBold=False):
        if isBold:
            self.set_font('Arial', 'B', size=font_size)
        else:
            self.set_font('Arial', size=font_size)

    def add_text(self, text, height, width, pdf_h):
        self.set_xy(height, width)
        self.cell(w=0, h=0, txt=text, border=0)
        if width > pdf_h - 30:
            self.add_page()
            width = 30
        else:
            width += 10
        return width

    def rescale_image_width_height(self, w, h, epw):
        new_w = 0.4 * epw
        new_h = new_w / w * h
        return new_w, new_h

    def add_image_basic(self, img, h, w, page_width):
        self.image(img, h=h, w=w)

    def add_image(self, im_jpg, height, width, pdf_h, h, w):
        if width > pdf_h - 100:
            self.add_page()
            width = 30
        self.set_xy(height, width)
        self.image(im_jpg, h=h, w=w)
        if width > pdf_h - 30:
            self.add_page()
            width = 30
        else:
            width += (h + 10)
        return width
