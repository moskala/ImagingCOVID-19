# Kivy imports
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

# Python imports
import sys
import os
import logging

# Custom kivy widgets imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from DialogWidgets import SaveDialog
from ErrorPopup import ErrorPopup

# Implemented methods imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', "Methods")))
import Reports as reports


class ResultPopup(Popup):
    analysis = ObjectProperty(None)
    content = ObjectProperty(None)
    comments = ObjectProperty(None)

    _popup = None
    _error_popup = None

    def __init__(self, analysis):
        super().__init__()
        self.analysis = analysis

    def generate_report_pdf(self, folder, filename):
        # Check if any analysis has been made yet
        try:
            if self.analysis is None:
                print("No analysis has been made yet")
                self._popup.dismiss()
                return
            reports.generate_report_pdf(self.analysis, self.comments, folder, filename)
            if self._popup is not None:
                self._popup.dismiss()
        except Exception as error:
            logging.error(": " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def generate_report_csv(self, folder, filename):
        try:
            # Check if any analysis has been made yet
            if self.analysis is None:
                print("No analisys has been made yet")
                self._popup.dismiss()
                return
            reports.generate_report_csv(self.analysis, self.comments, folder, filename)
            if self._popup is not None:
                self._popup.dismiss()
        except Exception as error:
            logging.error(": " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def show_save_csv(self, comments):
        try:
            """This function runs save dialog"""
            self.comments = comments
            content = SaveDialog(save=self.generate_report_csv, cancel=self.my_dismiss)
            self._popup = Popup(title="Save file", content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()
        except Exception as error:
            logging.error(": " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def show_save_pdf(self, comments):
        """This function runs save dialog"""
        try:
            self.comments = comments
            content = SaveDialog(save=self.generate_report_pdf, cancel=self.my_dismiss)
            self._popup = Popup(title="Save file", content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()
        except Exception as error:
            logging.error(": " + str(error))
            self._error_popup = ErrorPopup(message=str(error))

    def my_dismiss(self):
        self._popup.dismiss()
