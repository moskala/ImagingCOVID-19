# Kivy imports
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

# Python imports
from pathlib import Path
import random
import sys
from joblib import load
import imageio
from datetime import date
from PIL import Image as PilImage
import pandas as pd
import os
import csv

# Custom kivy widgets imports
# sys.path.append(str(Path().resolve()))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.append(Path().resolve() / "CustomKivyWidgets")
from CustomKivyWidgets.DialogWidgets import SaveDialog

# Implemented methods imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', "Methods")))
from Pdf import *
from ImageClass import *
from net.testNet import Net
from PredictGLCM import *
from PredictAlexnet import *
from PredictHaralick import *
from Grayscale import *
from Analysis.Analysis import *
from Analysis.Result import *


class ResultPopup(Popup):
    analysis = ObjectProperty(None)
    content = ObjectProperty(None)
    comments = ObjectProperty(None)

    _popup = None

    def __init__(self, analysis):
        super().__init__()
        self.analysis = analysis

    def get_result_array(self, result, withHeaders=False):
        res = result.get_object_properties_list()
        res.pop(2)
        if withHeaders:
            headers = result.get_object_properties_headers()
            nres = np.asarray(res)
            nheaders = np.asarray(headers)
            # array with one result
            nres = np.column_stack((nheaders, nres))
            return nres
        else:
            return res

    def generate_report_pdf(self, folder, filename):
        print('comments ', self.comments)
        if (not '.pdf' in filename):
            filename += '.pdf'
        outputFile = folder + '/' + filename
        if (self.analysis is None):
            print("No analisys has been made yet")
            self._popup.dismiss()
            return
        else:
            dateStr = 'ImagingCOVID-19  -  Report generated on ' + date.today().strftime("%d/%m/%Y") + '\n'
            # pdf
            pdf = PDF()
            pdf.add_page()
            # width and height for A4
            pdf_w = 210
            pdf_h = 297
            font_size = 11
            epw = pdf.w - 2 * pdf.l_margin
            # title
            pdf.ln(font_size)
            pdf.set_font_characteristics(font_size=font_size, isBold=True)
            pdf.cell(epw, 0.0, dateStr, align='C')
            pdf.ln(3 * font_size)
            # set font
            pdf.set_font_characteristics(font_size=font_size)
            pdf.cell(epw, 0.0, 'Comments', align='C')
            pdf.ln(font_size)
            pdf.cell(epw, 0.0, self.comments, align='L')
            pdf.ln(font_size)
            rsnumbers = self.analysis.get_report_summary_numbers()
            rsheaders = self.analysis.get_report_summary_headers()
            rsnumbers = np.column_stack((rsheaders, rsnumbers))
            counter = 1
            for i in range(len(self.analysis.result_list)):
                if (len(self.analysis.result_list[i]) == 0):
                    continue
                how_many_slices_analized = len(self.analysis.result_list[i])
                how_many_slices_total = self.analysis.slices_number[i]
                how_many_results = self.analysis.calculate_results(i)
                sheaders = np.asarray(self.analysis.get_analysis_summary_headers())
                snumbers = np.asarray(
                    self.analysis.get_analysis_summary_numbers(how_many_slices_total, how_many_slices_analized,
                                                               how_many_results))
                snumbers = np.column_stack((sheaders, snumbers))
                pdf.cell(epw, 0.0, 'Examination details #' + str(counter), align='C')
                pdf.ln(font_size)
                diction = self.analysis.get_dictionary_by_method_from_list(i)
                for key in diction.keys():
                    parts = key.split(',')
                    if (len(parts) > 3):
                        pdf.cell(epw, 0.0,
                                 'Examination type: ' + parts[0] + ', Method: ' + parts[1] + ", CT Window: " + parts[
                                     2] + ", Classifier: " + parts[3], align='C')
                    else:
                        pdf.cell(epw, 0.0, 'Examination type: ' + parts[0] + ', Method: ' + parts[1], align='C')
                    pdf.ln(font_size)
                    for result in diction[key]:
                        if (diction[key].index(result) == 0):
                            # array with one result
                            nres = np.transpose(self.get_result_array(result, withHeaders=True))
                            for row in nres:
                                for col in row:
                                    if (list(row).index(col) == 0):
                                        pdf.cell(epw / 10, font_size, str(col), border=1)
                                    else:
                                        pdf.cell(9 * epw / 30, font_size, str(col), border=1)
                                pdf.ln(font_size)
                        else:
                            nres = np.transpose(self.get_result_array(result))
                            for col in nres:
                                if (list(nres).index(col) == 0):
                                    pdf.cell(epw / 10, font_size, str(col), border=1)
                                else:
                                    pdf.cell(9 * epw / 30, font_size, str(col), border=1)
                            pdf.ln(font_size)
                    pdf.ln(2 * font_size)
                    prev_file = ""
                    if (self.analysis.get_actual_analysis_total() <= 2 and len(diction[key]) < 5):
                        pdf.cell(epw, 0.0, 'Analized images', align='C')
                        pdf.ln(font_size)
                        for result in diction[key]:
                            res = result.get_object_properties_list()
                            lungs = res[2]
                            number = str(random.randint(0, 20000000))
                            temp_image = folder + '/test' + number + '.jpg'
                            if len(lungs.shape) > 2:
                                im = PilImage.fromarray(lungs, "RGB")
                            else:
                                lung_image = convert_array_to_grayscale(lungs)
                                im = Image.fromarray(lung_image)
                            im.save(temp_image)

                            parts = res[3].split('x')
                            h, w = pdf.rescale_image_width_height(int(parts[0]), int(parts[1]), epw)
                            pdf.add_image_basic(temp_image, h, w, pdf_w)
                            if (diction[key].index(result) % 2 == 0):
                                prev_file = res[1]
                            else:
                                pdf.ln(font_size)
                                pdf.cell(epw, 0.0, 'File name: ' + prev_file, align='L', ln=0)
                                pdf.cell(epw, 0.0, 'File name: ' + res[1], align='R')
                                pdf.ln(font_size)
                            os.remove(temp_image)

                pdf.ln(3 * font_size)
                pdf.cell(epw, 0.0, 'Examination summary', align='C')
                pdf.ln(font_size)
                for row in snumbers:
                    for col in row:
                        pdf.cell(epw / 2, font_size, str(col), border=1)
                    pdf.ln(font_size)
                pdf.ln(3 * font_size)
                counter += 1
            # report summary
            pdf.cell(epw, 0.0, 'Report summary', align='C')
            pdf.ln(font_size)
            for row in rsnumbers:
                for col in row:
                    pdf.cell(epw / 2, font_size, str(col), border=1)
                pdf.ln(font_size)
            # saving
            pdf.output(outputFile, 'F')
            self._popup.dismiss()

    def get_results_dataframe(self):
        all_examinations = self.analysis.result_list
        df_results = pd.DataFrame()
        additional_headers = ["ExamId", "ExamType", "Classifier"]
        for i in range(0, len(all_examinations)):
            results = [(result.get_object_properties_headers() + additional_headers,
                        result.get_object_properties_list_without_image() + [i + 1,
                                                                             str(result.get_examination_type()),
                                                                             result.get_method_name()])
                       for result in all_examinations[i]]
            rows = [dict(zip(key, val)) for key, val in results]
            df_results = df_results.append(rows)

        df_results = df_results[["ExamId", "ExamType", "File name", "Layer no", "Image size", "Classifier", "Result"]]

        return df_results

    def get_severity_summary_dataframe(self, df_results):

        df_severity = df_results.loc[df_results["Classifier"] == "Severity score"].copy()

        if len(df_severity.index) > 0:
            df_severity["Result"] = df_severity["Result"].apply(lambda x: x[1])
            summary = df_severity.groupby("Result").size()
            df_severity_summary = summary.to_frame().reset_index()
            df_severity_summary.columns = ["Severity score", "Number of cases"]
            return df_severity_summary
        else:
            return None

    def get_classification_summary_dataframe(self, df_results):

        normal = 0
        covid = 0
        uncertain = 0

        groups = list((df_results.groupby("ExamId")))

        for group in groups:
            df = group[-1]
            severity_results = df[df["Classifier"] == "Severity score"]
            if severity_results.shape[0] > 0:
                score = np.any(list(severity_results["Result"].apply(lambda x: x[1])))
                covid += score
                normal += not score
            else:
                slices = list(df.loc[df["Classifier"] != "Severity score"].groupby(["File name", "Layer no"]))
                for s in slices:
                    result = np.unique(s[-1][["Result"]])
                    if len(result) != 1:
                        uncertain += 1
                    elif "Normal" in result:
                        normal += 1
                    elif "COVID-19" in result:
                        covid += 1

        total = self.analysis.get_actual_analysis_total()
        summary_numbers = [total, normal, covid, uncertain]
        summary_headers = self.analysis.get_report_summary_headers()
        return pd.DataFrame([summary_numbers], columns=summary_headers)

    def generate_report_csv(self, folder, filename):

        if self.analysis is None:
            print("No analisys has been made yet")
            self._popup.dismiss()
            return

        print('comments ', self.comments)
        if '.csv' not in filename:
            filename += '.csv'

        output_file = str(Path(folder) / filename)

        title = 'ImagingCOVID-19  -  Report generated on ' + date.today().strftime("%d/%m/%Y") + '\n'

        df_results = self.get_results_dataframe()

        df_covid_summary = self.get_classification_summary_dataframe(df_results)

        df_severity_summary = self.get_severity_summary_dataframe(df_results)

        with open(output_file, mode='w') as analysis_file:
            # add title
            analysis_file.write(title)
            analysis_file.write('\n')
            analysis_file.write('Comments\n')
            if self.content is not None:
                analysis_file.write(self.comments)
                analysis_file.write('\n')
            analysis_file.write('\n')
            analysis_file.write('Examination details\n')
            analysis_file.write('\n')

        # add all results
        df_results.to_csv(output_file, index=False, mode='a')

        with open(output_file, "a") as analysis_file:
            analysis_file.write('\n')
            analysis_file.write('Examinations summary\n')
            analysis_file.write('\n')

        # add examinations summary
        df_covid_summary.to_csv(output_file, index=False, mode='a')

        if df_severity_summary is not None:
            with open(output_file, "a") as analysis_file:
                analysis_file.write('\n')
                analysis_file.write('Severity summary\n')
                analysis_file.write('\n')
            # add severity summary
            df_severity_summary.to_csv(output_file, index=False, mode='a')

        if self._popup is not None:
            self._popup.dismiss()

    def show_save_csv(self, comments):
        """This function runs save dialog"""
        self.comments = comments
        content = SaveDialog(save=self.generate_report_csv, cancel=self.my_dismiss)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save_pdf(self, comments):
        """This function runs save dialog"""
        self.comments = comments
        content = SaveDialog(save=self.generate_report_pdf, cancel=self.my_dismiss)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def my_dismiss(self):
        self._popup.dismiss()
