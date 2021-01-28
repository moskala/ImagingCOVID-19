# Python imports
import random
import sys
from datetime import date
from PIL import Image
import pandas as pd
import numpy as np
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Pdf import *
from Grayscale import convert_array_to_grayscale
from Analysis.Result import *


def get_result_array(result, with_headers=False):
    res = result.get_object_properties_list()
    res.pop(2)
    if with_headers:
        headers = result.get_object_properties_headers()
        nres = np.asarray(res)
        nheaders = np.asarray(headers)
        nres = np.column_stack((nheaders, nres))
        return nres
    else:
        return res


def get_results_dataframe(analysis):
    all_examinations = analysis.result_list
    df_results = pd.DataFrame()
    additional_headers = ["ExamId", "ExamType", "Classifier"]
    exam_counter = 1
    for i in range(0, len(all_examinations)):
        if len(all_examinations[i]) == 0:
            continue
        results = [(result.get_object_properties_headers() + additional_headers,
                    result.get_object_properties_list_without_image() + [exam_counter,
                                                                         str(result.get_examination_type()),
                                                                         result.get_method_name()])
                   for result in all_examinations[i]]
        rows = [dict(zip(key, val)) for key, val in results]
        df_results = df_results.append(rows)
        exam_counter += 1

    df_results = df_results[["ExamId", "ExamType", "File name", "Layer no", "Image size", "Classifier", "Result"]]

    return df_results


def get_severity_summary_dataframe(df_results):

    df_severity = df_results.loc[df_results["Classifier"] == "Severity score"].copy()

    if len(df_severity.index) > 0:
        df_severity["Result"] = df_severity["Result"].apply(lambda x: x[1])
        summary = df_severity.groupby("Result").size()
        df_severity_summary = summary.to_frame().reset_index()
        df_severity_summary.columns = ["Severity score", "Number of layers"]
        return df_severity_summary
    else:
        return None


def get_examintaion_summary_dataframe(analysis, df_results, exam_id, slices_total):
    normal = 0
    covid = 0
    uncertain = 0

    df_exam = df_results.loc[df_results["ExamId"] == exam_id].copy()

    groups = df_exam.groupby(["File name", "Layer no"])

    total = len(groups)

    for layer in groups:
        df = layer[-1]
        severity_results = df[df["Classifier"] == "Severity score"]
        if severity_results.shape[0] > 0:
            score = np.any(list(severity_results["Result"].apply(lambda x: x[1])))
            covid += score
            normal += not score
        else:
            result = np.unique(df[["Result"]])
            if len(result) != 1:
                uncertain += 1
            elif "Normal" in result:
                normal += 1
            elif "COVID-19" in result:
                covid += 1

    summary_numbers = [slices_total, total, covid, normal, uncertain]
    summary_headers = analysis.get_analysis_summary_headers()
    return pd.DataFrame([summary_numbers], columns=summary_headers)


def get_classification_summary_dataframe(analysis, df_results):

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

    total = analysis.get_actual_analysis_total()
    summary_numbers = [total, normal, covid, uncertain]
    summary_headers = analysis.get_report_summary_headers()
    return pd.DataFrame([summary_numbers], columns=summary_headers)


def generate_report_pdf(analysis, comments, folder, filename):

    # Check if filename has extension
    if '.pdf' not in filename:
        filename += '.pdf'

    output_file = str(Path(folder) / filename)

    title = 'ImagingCOVID-19'
    title_time = 'Report generated on ' + date.today().strftime("%d/%m/%Y") + '\n'

    # pdf settings
    pdf = PDF()
    pdf.add_page()

    # width and height for A4
    pdf_w = 210
    pdf_h = 297
    font_size = 11
    epw = pdf.w - 2 * pdf.l_margin

    # write title
    pdf.ln(font_size)
    pdf.set_font_characteristics(font_size=1.5*font_size, isBold=True)
    pdf.cell(epw, 0.0, title, align='C')
    # set font
    pdf.set_font_characteristics(font_size=font_size)
    pdf.ln(font_size)
    pdf.cell(epw, 0.0, title_time, align='C')
    pdf.ln(3 * font_size)

    # write comments
    pdf.cell(epw, 0.0, 'Comments', align='C')
    pdf.ln(font_size)
    if comments is not None:
        pdf.cell(epw, 0.0, comments, align='L')
    else:
        pdf.cell(epw, 0.0, ' ', align='L')
    pdf.ln(font_size)

    counter = 1

    for i in range(len(analysis.result_list)):
        if len(analysis.result_list[i]) == 0:
            continue

        # write examination details
        pdf.set_font_characteristics(font_size=1.2 * font_size, isBold=True)
        pdf.cell(epw, 0.0, 'Case #' + str(counter), align='C')
        pdf.set_font_characteristics(font_size=font_size)
        pdf.ln(font_size)
        diction = analysis.get_dictionary_by_method_from_list(i)
        for key in diction.keys():
            parts = key.split(',')

            # write examination subtitle
            pdf.cell(epw, 0.0, ''.join(['Examination type: ', parts[0], '\n']), align='L')
            pdf.ln(0.5*font_size)
            pdf.cell(epw, 0.0, ''.join(['Method:  ', parts[1], '\n']), align='L')
            pdf.ln(0.5 * font_size)
            pdf.cell(epw, 0.0, ''.join(['CT Window: ', parts[2], '\n']), align='L')
            if len(parts) > 3:
                pdf.ln(0.5 * font_size)
                pdf.cell(epw, 0.0, ''.join(['Classifier: ', parts[3], '\n']), align='L')

            pdf.ln(font_size)

            for result in diction[key]:
                if diction[key].index(result) == 0:
                    # array with one result
                    nres = np.transpose(get_result_array(result, with_headers=True))
                    for row in nres:
                        for col in row:
                            if list(row).index(col) == 0:
                                pdf.cell(epw / 10, font_size, str(col), border=1)
                            else:
                                pdf.cell(9 * epw / 30, font_size, str(col), border=1)
                        pdf.ln(font_size)
                else:
                    nres = np.transpose(get_result_array(result))
                    for col in nres:
                        if list(nres).index(col) == 0:
                            pdf.cell(epw / 10, font_size, str(col), border=1)
                        else:
                            pdf.cell(9 * epw / 30, font_size, str(col), border=1)
                    pdf.ln(font_size)
            pdf.ln(2 * font_size)
            prev_file = ""
            # Add analyzed images
            if (analysis.get_actual_analysis_total() <= 2 and len(diction[key]) < 5) or (len(diction[key]) < 2):
                pdf.cell(epw, 0.0, 'Analyzed images', align='C')
                pdf.ln(font_size)

                for result in diction[key]:
                    res = result.get_object_properties_list()
                    lungs = res[2]
                    number = str(random.randint(0, 20000000))
                    temp_image = folder + '/test' + number + '.jpg'
                    if len(lungs.shape) > 2:
                        im = Image.fromarray(lungs, "RGB")
                    else:
                        lung_image = convert_array_to_grayscale(lungs)
                        im = Image.fromarray(lung_image)
                    im.save(temp_image)

                    parts = res[3].split('x')
                    h, w = pdf.rescale_image_width_height(int(parts[0]), int(parts[1]), epw)
                    pdf.add_image_basic(temp_image, h, w, pdf_w)
                    pdf.ln(font_size)
                    pdf.cell(epw, 0.0, 'File name: ' + res[1], align='L')
                    pdf.ln(font_size)
                    os.remove(temp_image)

        # get single analysis summary
        df_results = get_results_dataframe(analysis)

        df_examination = df_results.loc[df_results["ExamId"] == (i+1)].copy()

        how_many_slices_total = analysis.slices_number[i]

        df_covid_summary = get_examintaion_summary_dataframe(analysis, df_results, counter, how_many_slices_total)
        # get severity summary or none
        df_severity_summary = get_severity_summary_dataframe(df_examination)

        df_covid_summary = df_covid_summary.transpose().reset_index()

        # write examination summary

        pdf.cell(epw, 0.0, 'Case summary', align='C')
        pdf.ln(font_size)
        for row in range(df_covid_summary.shape[0]):
            for item in df_covid_summary.iloc[row]:
                pdf.cell(epw / 2, font_size, str(item), border=1)
            pdf.ln(font_size)

        counter += 1

        if df_severity_summary is not None:
            pdf.ln(1 * font_size)
            pdf.cell(epw, 0.0, 'Severity summary', align='C')
            pdf.ln(font_size)
            headers = list(df_severity_summary.columns)
            for h in headers:
                pdf.cell(epw / 2, font_size, str(h), border=1)
            pdf.ln(font_size)
            for row in range(df_severity_summary.shape[0]):
                for item in df_severity_summary.iloc[row]:
                    pdf.cell(epw / 2, font_size, str(item), border=1)
                pdf.ln(font_size)
            pdf.ln(font_size)

        pdf.ln(2*font_size)

    pdf.add_page()
    # write title of summary
    pdf.ln(font_size)
    pdf.set_font_characteristics(font_size=1.2*font_size, isBold=True)
    pdf.cell(epw, 0.0, "Complete report summary", align='C')
    pdf.set_font_characteristics(font_size=font_size)
    pdf.ln(font_size)


    # get report classification summary
    df_summary = get_classification_summary_dataframe(analysis, df_results)
    df_summary = df_summary.transpose().reset_index()

    # Write report summary
    pdf.cell(epw, 0.0, 'Report summary', align='C')
    pdf.ln(font_size)
    for row in range(df_summary.shape[0]):
        for item in df_summary.iloc[row]:
            pdf.cell(epw / 2, font_size, str(item), border=1)
        pdf.ln(font_size)

    # get report severity summary
    df_severity = get_severity_summary_dataframe(df_results)

    if df_severity is not None:
        pdf.ln(1 * font_size)
        pdf.cell(epw, 0.0, 'Summary of severity score', align='C')
        pdf.ln(font_size)
        headers = list(df_severity.columns)
        for h in headers:
            pdf.cell(epw / 2, font_size, str(h), border=1)
        pdf.ln(font_size)
        for row in range(df_severity.shape[0]):
            for item in df_severity.iloc[row]:
                pdf.cell(epw / 2, font_size, str(item), border=1)
            pdf.ln(font_size)
        pdf.ln(font_size)

    # saving
    pdf.output(output_file, 'F')


def generate_report_csv(analysis, comments, folder, filename):

    if '.csv' not in filename:
        filename += '.csv'

    output_file = str(Path(folder) / filename)

    title = 'ImagingCOVID-19  -  Report generated on ' + date.today().strftime("%d/%m/%Y") + '\n'

    df_results = get_results_dataframe(analysis)

    df_covid_summary = get_classification_summary_dataframe(analysis, df_results)

    df_severity_summary = get_severity_summary_dataframe(df_results)

    with open(output_file, mode='w') as analysis_file:
        # add title
        analysis_file.write(title)
        analysis_file.write('\n')
        analysis_file.write('Comments\n')
        if comments is not None:
            analysis_file.write(comments)
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

