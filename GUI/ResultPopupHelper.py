from Pdf import *
import csv
import imageio
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty


def calculate_results(analysis):
    how_many_results = [0,0,0] #0-normal,1-covid,2-undefined
    for key in analysis.dictionary:
        how_many_results_temp = [0,0]
        for result in analysis.dictionary[key]:
            if(result_str=='COVID-19'):
                how_many_results_temp[1]+=1
            elif(result_str=='Normal'):
                how_many_results_temp[0]+=1
        if(how_many_results_temp[0]>0 and how_many_results_temp[1]==0):
            how_many_results[0]+=1
        elif(how_many_results_temp[1]>0 and how_many_results_temp[0]==0):
            how_many_results[1]+=1
        else:
            how_many_results[2]+=1
    return how_many_results
def generate_report(folder,filename,analysis):
    outputFile = folder+'/'+filename
    if(filename.__contains__('.csv')):
        with open(outputFile, mode='w') as analysis_file:
            analysis_writer = csv.writer(analysis_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if(analysis is None):
                print("No analisys has been made yet")
                return
            for result in analysis.result_list:
                file_name, lung_image, image_height, image_width, scale, result_str = result.get_object_properties()
                method = result.get_method_name()
                analysis_writer.writerow(['Analysis no: ',analysis.result_list.index(result)])
                analysis_writer.writerow(['File name', file_name])
                analysis_writer.writerow(['Image height', image_height])
                analysis_writer.writerow(['Image width', image_width])
                analysis_writer.writerow(['CT Window Type', scale])
                analysis_writer.writerow(['Method', method])
                analysis_writer.writerow(['Result', result_str])
                analysis_writer.writerow([])
            # summary
            analysis_writer.writerow([])
            analysis_writer.writerow(['Summary'])
            how_many_slices_analized = len(analysis.dictionary.keys())
            how_many_slices_total = analysis.slices_number
            how_many_results =calculate_results()
            analysis_writer.writerow(['Number of analyzed layers',str(how_many_slices_analized)+"/"+str(how_many_slices_total)])    
            analysis_writer.writerow(['COVID-19 layers',str(how_many_results[1])+"/"+str(how_many_slices_analized)])   
            analysis_writer.writerow(['Normal layers',str(how_many_results[0])+"/"+str(how_many_slices_analized)])
            analysis_writer.writerow(['Uncertain layers',str(how_many_results[2])+"/"+str(how_many_slices_analized)])
    else: #pdf
        pdf = PDF()
        pdf.add_page()
        # width and height for A4
        pdf_w=210
        pdf_h=297
        w_offset = 10.0
        h_offset = 30.0
        difference = 10.0
        # set font
        pdf.set_font_characteristics()
        if(analysis is None):
            print("No analisys has been made yet")
            return
        for result in analysis.result_list:
            file_name, lung_image, image_height, image_width, scale, result_str = result.get_object_properties()
            method = result.get_method_name()
            analysis_no = 'Analysis no: '+ str(1+analysis.result_list.index(result))
            h_offset=pdf.add_text(analysis_no,w_offset,h_offset,pdf_h)
            
            flnm = 'File name: ' + file_name
            h_offset=pdf.add_text(flnm,w_offset,h_offset,pdf_h)
            # zdjecie
            lung_image = convert_array_to_grayscale(lung_image)
            im = Image.fromarray(lung_image)
            temp_image = folder+'/test.jpg'
            imageio.imwrite(temp_image, lung_image)
            h_offset=pdf.add_image(temp_image,w_offset,h_offset,pdf_h,image_height/5,image_width/5)
            os.remove(temp_image)
            #
            ih = 'Image height: ' + str(image_height)
            h_offset=pdf.add_text(ih,w_offset,h_offset,pdf_h)
            iw = 'Image width: '+ str(image_width)
            h_offset=pdf.add_text(iw,w_offset,h_offset,pdf_h)
            
            s = 'CT Window Type: '+ str(scale)
            h_offset=pdf.add_text(s,w_offset,h_offset,pdf_h)
            
            m = 'Method: '+ method
            h_offset=pdf.add_text(m,w_offset,h_offset,pdf_h)
            
            r = 'Result: '+ result_str
            h_offset=pdf.add_text(r,w_offset,h_offset,pdf_h)
            if(h_offset!=30):
                h_offset+=difference*2
        #saving
        pdf.output(outputFile,'F')
    
