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

# Custom kivy widgets imports
# sys.path.append(str(Path().resolve()))
sys.path.append(Path().resolve() / "CustomKivyWidgets")
from CustomKivyWidgets.DialogWidgets import SaveDialog

# Implemented methods imports
sys.path.append(str(Path().resolve().parent.parent / "Methods"))
from Pdf import *
from LungSegmentation.LungSegmentation_MethodA_dicom import SegmentationA
from LungSegmentation.LungSegmentation_MethodB_dicom import SegmentationB
import LungSegmentation.LungSegmentation_MethodKMeans_AllTypes as segmentation
import PlotUtilities as show
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
    def __init__(self,analysis):
        super().__init__()
        self.analysis = analysis
    def calculate_results(self):
        how_many_results = [0,0,0] #0-normal,1-covid,2-undefined
        for key in self.analysis.dictionary:
            how_many_results_temp = [0,0]
            for result in self.analysis.dictionary[key]:
                if(result=='COVID-19'):
                    how_many_results_temp[1]+=1
                elif(result=='Normal'):
                    how_many_results_temp[0]+=1
            if(how_many_results_temp[0]>0 and how_many_results_temp[1]==0):
                how_many_results[0]+=1
            elif(how_many_results_temp[1]>0 and how_many_results_temp[0]==0):
                how_many_results[1]+=1
            else:
                how_many_results[2]+=1
        return how_many_results
    def get_result_array(self,result,withHeaders = False):
        res = result.get_object_properties_list()
        res.pop(1)
        res.insert(0,self.analysis.result_list.index(result)+1)
        if(withHeaders):
            headers = result.get_object_properties_headers()
            nres = np.asarray(res)
            nheaders = np.asarray(headers)
            # array with one result
            nres = np.column_stack((nheaders,nres))
            return nres
        else:
            return res

    def generate_report_pdf(self,folder,filename):
        print('comments ',self.comments)
        outputFile = folder+'/'+filename
        if(self.analysis is None):
                print("No analisys has been made yet")
                self._popup.dismiss()
                return
        else:
            dateStr = 'Report generated on '+date.today().strftime("%d/%m/%Y")+'\n'
            how_many_slices_analized = len(self.analysis.dictionary.keys())
            how_many_slices_total = self.analysis.slices_number
            how_many_results = self.calculate_results()
            sheaders = np.asarray(self.analysis.get_analysis_summary_headers())
            snumbers = np.asarray(self.analysis.get_analysis_summary_numbers(how_many_slices_total,how_many_slices_analized,how_many_results))
            snumbers = np.column_stack((sheaders,snumbers))
             #pdf
            pdf = PDF()
            pdf.add_page()
            # width and height for A4
            pdf_w=210
            pdf_h=297
            font_size = 11
            epw = pdf.w - 2*pdf.l_margin
            # title
            pdf.ln(font_size)
            pdf.set_font_characteristics(font_size=font_size,isBold=True)
            pdf.cell(epw, 0.0, dateStr, align='C')
            pdf.ln(3*font_size)
            # set font
            pdf.set_font_characteristics(font_size=font_size)
            pdf.cell(epw, 0.0, 'Comments', align='C')
            pdf.ln(font_size)
            pdf.cell(epw, 0.0, self.comments, align='L')
            pdf.ln(font_size)
            pdf.cell(epw, 0.0, 'Analysis details', align='C')
            pdf.ln(font_size)
            diction = self.analysis.get_dictionary_by_method_from_list()
            for key in diction.keys():
                parts = key.split(',')
                pdf.cell(epw,0.0,'Method: '+parts[0]+", CT Window: "+parts[1],align='C')
                pdf.ln(font_size)
                for result in diction[key]:
                    if(diction[key].index(result)==0):
                        # array with one result
                        nres = np.transpose(self.get_result_array(result,withHeaders=True))
                        for row in nres:
                            for col in row:
                                if(list(row).index(col)==0):
                                    pdf.cell(epw/14, font_size, str(col), border=1)
                                else:
                                    pdf.cell(13*epw/42, font_size, str(col), border=1)
                            pdf.ln(font_size)
                    else:
                        nres = np.transpose(self.get_result_array(result))
                        for col in nres:
                            if(list(nres).index(col)==0):
                                pdf.cell(epw/14, font_size, str(col), border=1)
                            else:
                                pdf.cell(13*epw/42, font_size, str(col), border=1)
                        pdf.ln(font_size)
                pdf.ln(2*font_size)
            
                pdf.cell(epw, 0.0, 'Analized images', align='C')
                pdf.ln(font_size)
                for result in diction[key]:
                    res = result.get_object_properties_list()
                    lungs = res[1]
                    lung_image = convert_array_to_grayscale(lungs)
                    im = Image.fromarray(lung_image)
                    number = str(random.randint(0,20000000))
                    print(number)
                    temp_image = folder+'/test'+number+'.jpg'
                    imageio.imwrite(temp_image, lung_image)
                    parts = res[2].split('x')
                    pdf.add_image_basic(temp_image,int(parts[0])/5,int(parts[1])/5,pdf_w)
                    pdf.ln(font_size)
                    pdf.cell(epw,0.0,'File name: '+res[0],align='L')
                    os.remove(temp_image)
                    pdf.ln(font_size)

            pdf.ln(3*font_size)
            pdf.cell(epw, 0.0, 'Summary', align='C')
            pdf.ln(font_size)
            for row in snumbers:
                for col in row:
                    pdf.cell(epw/2, font_size, str(col), border=1)
                pdf.ln(font_size)
            #saving
            pdf.output(outputFile,'F')
            self._popup.dismiss()

    def generate_report_csv(self,folder,filename):
        print('comments ',self.comments)
        outputFile = folder+'/'+filename
        if(self.analysis is None):
                print("No analisys has been made yet")
                self._popup.dismiss()
                return
        else:
            dateStr = 'Report generated on '+date.today().strftime("%d/%m/%Y")+'\n'
            how_many_slices_analized = len(self.analysis.dictionary.keys())
            how_many_slices_total = self.analysis.slices_number
            how_many_results = self.calculate_results()
            sheaders = np.asarray(self.analysis.get_analysis_summary_headers())
            snumbers = np.asarray(self.analysis.get_analysis_summary_numbers(how_many_slices_total,how_many_slices_analized,how_many_results))
            snumbers = np.column_stack((sheaders,snumbers))

            with open(outputFile, mode='w') as analysis_file:
                # add title
                analysis_file.write(dateStr)
                analysis_file.write('\n')
                analysis_file.write('Comments\n')
                analysis_file.write(self.comments)
                analysis_file.write('\n')
                analysis_file.write('\n')
                analysis_file.write('Analysis details\n')
                analysis_file.write('\n')
                # add all results
                for result in self.analysis.result_list:
                    # array with one result
                    nres = self.get_result_array(result,withHeaders=True)
                    np.savetxt(analysis_file,nres,delimiter=',',fmt='%s')
                    analysis_file.write("\n")
                # summary
                analysis_file.write('\n')
                analysis_file.write('Summary\n')
                analysis_file.write('\n')
                np.savetxt(analysis_file,snumbers,delimiter=',',fmt='%s')
                analysis_file.write("\n")
                self._popup.dismiss()

    def show_save_csv(self,comments):
        """This function runs save dialog"""
        self.comments=comments
        content = SaveDialog(save=self.generate_report_csv,  cancel=self.my_dismiss)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save_pdf(self,comments):
        """This function runs save dialog"""
        self.comments=comments
        content = SaveDialog(save=self.generate_report_pdf,  cancel=self.my_dismiss)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def my_dismiss(self):
        self._popup.dismiss()

