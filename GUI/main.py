# Kivy imports
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

# Python imports
from pathlib import Path
import sys
import os
import logging
import copy

# Custom kivy widgets imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'CustomKivyWidgets')))
from AnalysisPopup import AnalysisPopup
from DialogWidgets import LoadDialog, SaveDialog
from DrawLesionsWidgets import DrawFigure, DrawPopup
from ErrorPopup import ErrorPopup
from LayersPopup import LayersPopup
from LungSegmentationPopup import LungSegmentationPopup
from ResultPopupWidget import ResultPopup
from ShowImageWidget import MyFigure, START_IMAGE

# Implemented methods imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Methods')))
from ImageMedical.ImageClass import ImageType, DicomImage, NiftiImage, JpgImage, PngImage
from ImageMedical.CTImageClass import CTDicomImage, CTNiftiImage, CTJpgImage, CTPngImage
from ImageMedical.XRayImageClass import XRayJpgImage, XRayPngImage
from CovidCTNet.testNet import Net
from ChooseSlices import LayerChoice
from Analysis.Analysis import Analysis
from Analysis.Result import NeuralNetworkResult, SeverityResult
from ExaminationType import ExaminationType
from LungSegmentation.LungSegmentationUtilities import draw_lines_on_image

# Paths
GUI_FOLDER = os.path.abspath(os.path.dirname(__file__))


class RootWidget(FloatLayout):
    """This class contains the root element for gui and all the necessary methods"""
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    image = ObjectProperty(None)
    result_grid = ObjectProperty(None)

    plot = None
    result = None

    image_object = CTJpgImage(GUI_FOLDER, START_IMAGE)

    _popup = None
    _draw_figure = None
    _draw_popup = None
    _error_popup = None
    analysis = None

    current_model = None
    analysis_popup = None
    layers_popup = None

    layer_choice = LayerChoice()

    examination_type = None

    def draw_lesions(self):
        """
        Function creates draw lesions popup and binds needed functions.
        :return: None
        """
        try:
            self._draw_figure = None
            popup = DrawPopup()
            popup.title = self.image_object.src_filename
            box = popup.ids.draw_panel
            fig = DrawFigure(image_data=self.image_object.get_image_to_draw())
            box.add_widget(fig, canvas='before')
            popup.ids.add_region_button.bind(on_release=fig.add_new_region)
            popup.ids.delete_region_button.bind(on_release=fig.delete_current_region)
            popup.bind(on_dismiss=fig.delete_source_file)
            self._draw_figure = fig
            self._draw_popup = popup
            self._draw_popup.open()
        except Exception as error:
            logging.error("Draw lesions: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def get_marked_lesions(self, *args):
        """
        Function is called when draw popup is being dismissed.
        Function reads coordinates of marked lesions from drawing figure.
        :param args: arguments passed by on_dismiss callback
        :return:
        """
        try:
            regions = self._draw_figure.finish_drawing()
            percentage, score = self.image_object.calculate_severity(regions)
            result = (percentage, score)
            result_text = str("Volume: {:.2f}%, Severity: {}".format(percentage, score))
            image_with_points = draw_lines_on_image(self.image_object.get_image_to_draw(), regions)
            self.analysis.add_to_list(SeverityResult(result,
                                                     image_with_points,
                                                     self.image_object.get_info(),
                                                     self.image_object.get_current_slice_number_to_show(),
                                                     self.examination_type))
            self._popup = Popup(title="Severity score",
                                content=Label(text=result_text),
                                size_hint=(0.6, 0.6),
                                auto_dismiss=True)
            self._popup.open()
        except Exception as error:
            logging.error("Get marked lesions: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def automatic_layer_choice(self):
        """
        Function opens LayersPopup.
        :return: None
        """
        try:
            self.layers_popup = LayersPopup(self.layer_choice,
                                            max_layers_range=self.image_object.total_slice_number)
            self.layers_popup.open()
        except Exception as error:
            logging.error("Layer choice popup: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def save_layer_selection(self, *args):
        """
        Function sets layers selection to layer_choice and closes popup.
        :return: None
        """
        try:
            settings = self.layers_popup.get_settings()
            if settings is not None:
                self.layer_choice = settings
                self.layers_popup.dismiss()
        except Exception as error:
            logging.error("Save layer selection: "+str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def layer_selection(self):
        """
        Function adds single layer to layers collection and sets text of button.
        :return: None
        """
        try:
            number = self.image_object.current_slice_number
            if self.layer_choice.check_collection_layer(number):
                self.layer_choice.remove_collection_layer(number)
            else:
                self.layer_choice.append_collection_layer(number)
            self.set_layers_button()
        except Exception as error:
            logging.error("Layers selection: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def set_layers_button(self):
        """
        Function sets button text depending on whether layer is already in layers collection.
        :return: None
        """
        try:
            if self.layer_choice.check_collection_layer(self.image_object.current_slice_number):
                self.add_remove_layer.text = "Remove layer\nfrom analysis"
            else:
                self.add_remove_layer.text = "Add layer\nto analysis"
        except Exception as error:
            logging.error("Layers button change: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def reset_layers_choice(self):
        """
        Function resets layers choice. Should be call when new image is being loaded.
        :return: None
        """
        try:
            self.layer_choice = LayerChoice()
            self.set_layers_button()
        except Exception as error:
            logging.error("Reset layer choice: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def slider_changed_value(self, value):
        """This function changes the displayed image when the slider is moved"""
        try:
            slice_number = int(value)
            if self.plot is not None and self.image_object is not None:
                self.left_panel.remove_widget(self.plot)
                self.plot = MyFigure(image_data=self.image_object.get_next_slice(slice_number))
                self.left_panel.add_widget(self.plot)
                self.slices_info.text = "Layer: {0}/{1}".format(self.image_object.get_current_slice_number_to_show(),
                                                                self.image_object.total_slice_number)
                self.set_layers_button()
                self.layer_choice.update_choice_singular(self.image_object.current_slice_number)
        except Exception as error:
            logging.error("Slider changed: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def load_next_slice(self, value):
        """This function changes the displayed image when the buttons 'Next' and 'Prev" are pressed"""
        try:
            shift = int(value)
            if self.plot is not None and self.image_object is not None:
                slice_number = self.image_object.current_slice_number + shift
                self.left_panel.remove_widget(self.plot)
                self.plot = MyFigure(image_data=self.image_object.get_next_slice(slice_number))
                self.left_panel.add_widget(self.plot)
                self.slices_info.text = "Layer: {0}/{1}".format(self.image_object.get_current_slice_number_to_show(),
                                                                self.image_object.total_slice_number)
                self.slider.value = self.image_object.current_slice_number
                self.set_layers_button()
                self.layer_choice.update_choice_singular(self.image_object.current_slice_number)
        except Exception as error:
            logging.error("Load next slice: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def dismiss_popup(self):
        """This function closes popup windows"""
        if self._popup is not None:
            self._popup.dismiss()

    def neural_network(self):
        """This function runs the neural network process for the displayed image"""
        try:
            if self.image_object.file_type == ImageType.JPG or self.image_object.file_type == ImageType.PNG:
                predict = Net.testImage(self.image_object.get_file_path())
                if predict == 'normal':
                    prediction = 'Normal'
                else:
                    prediction = 'COVID-19'
                if self.analysis is None:
                    self.analysis = Analysis(slices_number=self.image_object.total_slice_number)
                self.add_result_to_analysis_neural_network(prediction,
                                                           self.image_object.get_current_slice_number_to_show())
                logging.debug('Added neural network result to reports: ')
            else:
                prediction = "Network accepts only jpg or png files!"

            popup = Popup(title='Result',
                          content=Label(text=prediction),
                          size=(400, 400),
                          size_hint=(None, None))
            popup.open()
        except Exception as error:
            logging.error("Neural network classification: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def lung_tissue_segmentation(self):
        """
        Functions opens segmentation popup with segmentation results.
        :return: None
        """
        try:
            popup = LungSegmentationPopup(self.image_object)
            popup.open()
        except Exception as error:
            logging.error("Lung segmentation: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def add_result_to_analysis_neural_network(self, prediction, layer_number):
        """
        Function add result of neural network analysis to all results.
        :param prediction: result prediction
        :param layer_number: number of analyzed layer
        :return: None
        """
        try:
            properties = self.image_object.get_info()
            result = NeuralNetworkResult(prediction,
                                         self.image_object.get_current_grayscale_slice(),
                                         properties["Height"],
                                         properties["Width"],
                                         properties["CT Window Type"],
                                         properties["Filename"],
                                         layer_number,
                                         self.examination_type)
            self.analysis.add_to_list(result)

            dict_key = properties["Filename"] + "_" + str(layer_number)
            if dict_key in self.analysis.dictionary[self.analysis.current_analysis_index]:
                self.analysis.dictionary[self.analysis.current_analysis_index][dict_key].append(prediction)
            else:
                temp_list = [prediction]
                self.analysis.dictionary[self.analysis.current_analysis_index].update({dict_key: temp_list})
            logging.debug('Added neural network result to reports: ')
        except Exception as error:
            logging.error("Neural network result: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def show_load(self):
        """This function runs load dialog"""
        try:
            content = LoadDialog(cancel=self.dismiss_popup)
            self._popup = Popup(title="Load file",
                                content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()
        except Exception as error:
            logging.error("Load dialog: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def show_save(self):
        """This function runs save dialog"""
        try:
            content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
            self._popup = Popup(title="Save file", content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()

        except Exception as error:
            logging.error("Save dialog: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def get_file_format(self, filename):
        """This function decides on the displayed image format"""
        try:
            ext = (filename.split('.'))[-1]
            if ext in DicomImage.file_extensions:
                return ImageType.DCM
            elif ext in NiftiImage.file_extensions:
                return ImageType.NIFTI
            elif ext in JpgImage.file_extensions:
                return ImageType.JPG
            elif ext in PngImage.file_extensions:
                return ImageType.PNG

        except Exception as error:
            logging.error("Check file format: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def update_analysis(self):
        """
        Function update analysis field. Should be call when new image is being loaded.
        :return: None
        """
        try:
            self.analysis.result_list.append([])
            self.analysis.dictionary.append({})
            self.analysis.current_analysis_index += 1
            self.analysis.slices_number.append(self.image_object.total_slice_number)

        except Exception as error:
            logging.error("Update analysis list: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def update_panel(self):
        """
        Function updates main panel by disabling buttons and adding figure.
        :return: None
        """
        try:
            if self.result is not None:
                self.left_panel.remove_widget(self.result)

            self.left_panel.remove_widget(self.plot)
            self.plot = MyFigure(image_data=self.image_object.get_current_slice())
            self.left_panel.add_widget(self.plot)
            self.slider.value = 0
            self.slider.step = 1
            self.slider.range = (0, self.image_object.total_slice_number - 1)
            self.slider.value_track = True

            self.slices_info.text = "Slice: {0}/{1}".format(self.image_object.get_current_slice_number_to_show(),
                                                            self.image_object.total_slice_number)
            self.dismiss_popup()
            # new layer choice initialization
            self.reset_layers_choice()
            self.examination_type_label.text = str(self.examination_type)

            if self.examination_type == ExaminationType.CT:
                disable = self.image_object.file_type != ImageType.JPG and self.image_object.file_type != ImageType.PNG
                self.ids.button_net.disabled = disable
            else:
                self.ids.button_net.disabled = True

        except Exception as error:
            logging.error("Update main panel: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def load_xray(self, path, filename):
        """
        Function loads X-Ray image from filesystem.
        :param path: path to selected file
        :param filename: filename of selected file
        :return: None
        """
        try:
            image_folder = path
            if not filename:
                raise ValueError('None file is selected.')
            image_file_name = str(Path(filename[0]).name)

            file_type = self.get_file_format(image_file_name)

            if file_type == ImageType.JPG:
                self.image_object = XRayJpgImage(image_folder, image_file_name)
            elif file_type == ImageType.PNG:
                self.image_object = XRayPngImage(image_folder, image_file_name)
            else:
                raise ValueError("Not supported file type")

            self.examination_type = ExaminationType.XRAY
            self.update_panel()
            self.dismiss_popup()
            self.update_analysis()
        except Exception as error:
            logging.error("Load X-Ray: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def load_ct(self, path, filename):
        """
        Function loads CT image from filesystem.
        :param path: path to selected file
        :param filename: filename of selected file
        :return: None
        """
        try:
            image_folder = path
            if not filename:
                raise ValueError('None file is selected.')
            image_file_name = str(Path(filename[0]).name)

            file_type = self.get_file_format(image_file_name)

            if file_type == ImageType.DCM:
                self.image_object = CTDicomImage(image_folder, image_file_name)
            elif file_type == ImageType.NIFTI:
                self.image_object = CTNiftiImage(image_folder, image_file_name)
            elif file_type == ImageType.JPG:
                self.image_object = CTJpgImage(image_folder, image_file_name)
            elif file_type == ImageType.PNG:
                self.image_object = CTPngImage(image_folder, image_file_name)
            else:
                print("Not supported file type")

            self.examination_type = ExaminationType.CT
            self.update_panel()
            self.dismiss_popup()
            self.update_analysis()

        except Exception as error:
            logging.error("Load CT: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def save(self, path, filename):
        """This function runs the saving process after pressing 'Save anonymized file' button"""
        try:
            success = self.image_object.save_anonymized_file(filename, path)
            if success:
                logging.info('Saving file: File saved')
            else:
                logging.warning('Saving file: File not saved')
            self.dismiss_popup()
        except Exception as error:
            logging.error("Save image: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def show_analysis_popup(self):
        """
        Function opens analysis popup and sets panel.
        :return: None
        """
        try:
            indexes = self.layer_choice.choose_indexes()
            if self.analysis_popup is not None:
                self.current_model = self.analysis_popup.current_model
            self.analysis_popup = AnalysisPopup(self.analysis,
                                                copy.deepcopy(self.image_object),
                                                self.current_model,
                                                self.examination_type,
                                                indexes)
            logging.debug("Current model: " + str(self.current_model))
            if self.current_model is None:
                self.analysis_popup.box_layout.add_widget(Label(text='None yet!'), index=9)
            else:
                bl = BoxLayout(orientation='horizontal')
                bl.add_widget(Label(text=str(type(self.current_model).__name__)))
                bl.add_widget(Button(text='Classify',
                                     on_release=self.analysis_popup.analysis_classify_recent))
                self.analysis_popup.box_layout.add_widget(bl, index=9)
            self.analysis_popup.open()
            self.current_model = self.analysis_popup.current_model

        except Exception as error:
            logging.error("Load analysis popup: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def show_result_popup(self):
        """
        Function creates adn show PopUp in application with some data about image.
        :return: None
        """
        try:
            popup = ResultPopup(analysis=self.analysis)

            popup.scroll_view.text = self.analysis.add_summary_to_text_element(isAll=True)
            popup.open()
        except Exception as error:
            logging.error("Result popup: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def __init__(self, *args, **kwargs):
        super(RootWidget, self).__init__(*args, **kwargs)
        try:
            self.image_object = CTJpgImage(GUI_FOLDER, START_IMAGE)
            self.examination_type = ExaminationType.CT
            # new analysis initialization
            self.analysis = Analysis(slices_number=self.image_object.total_slice_number)
        except Exception as error:
            logging.critical("Init root widget: " + str(error))
            self._error_popup = ErrorPopup(message=str(error))


class Main(App):
    pass


Factory.register('RootWidget', cls=RootWidget)
Factory.register('AnalysisPopup', cls=AnalysisPopup)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)
Factory.register('DrawFigure', cls=DrawFigure)
Factory.register('ErrorPopup', cls=ErrorPopup)
Factory.register('LayersPopup', cls=LayersPopup)
Factory.register('LungSegmentationPopup', cls=LungSegmentationPopup)
Factory.register('ResultPopup', cls=ResultPopup)
Factory.register('MyFigure', cls=MyFigure)


if __name__ == '__main__':
    Main().run()
