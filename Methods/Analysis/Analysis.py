

class Analysis:

    result_list = None
    dictionary = None

    def __init__(self, slices_number, lst=None):

        if lst is None:
            self.result_list = []
        else:
            self.result_list = lst
        self.result_list.append([])
        self.dictionary = []
        self.dictionary.append({})
        self.current_analysis_index = 0
        self.slices_number = []
        self.slices_number.append(slices_number)

    def add_to_list(self, result):
        self.result_list[self.current_analysis_index].append(result)

    def add_summary_to_text_element(self, isAll = False):
        counter = 1
        text_element = ""
        if isAll:
            for anal in self.result_list:
                if(len(self.result_list[self.result_list.index(anal)])==0):
                    continue
                text_element+='Examination #'+str(counter)+'\n'
                for result in anal:
                    res = result.get_object_properties_list()
                    string ='Layer no: '+ str(res[0]) +"    Result: "+ str(res[-1]) +'    Method: '+result.get_method_name()+'\n'
                    text_element+=string
                counter+=1
        else:
            text_element+='Examination #'+str(counter)+'\n'
            for result in self.result_list[self.current_analysis_index]:
                res = result.get_object_properties_list()
                string ='Layer no: '+ str(res[0]) +"    Result: "+ str(res[-1]) +'    Method: '+result.get_method_name()+'\n'
                text_element+=string
            counter+=1
        print(text_element)
        return text_element

    def get_dictionary_by_method_from_list(self, index):
        dictionary_method = {}
        for result in self.result_list[index]:
            examination_type = str(result.get_examination_type())
            ct_window = str(result.get_object_ct_window())
            classifier = str(result.get_classifier())
            method_name = result.get_method_name()
            method=examination_type
            if(len(method_name)>0):
                method+=str(","+method_name)
            if(ct_window is not None):
                method+=str(","+ct_window)
            if(len(classifier)>0):
                method+=str(","+classifier)
            
            if(dictionary_method.keys().__contains__(method)):
                dictionary_method[method].append(result)
            else:
                temp_list = [result]
                dictionary_method.update({method:temp_list})
        return dictionary_method

    def calculate_results(self, i):
        how_many_results = [0, 0, 0] #0-normal,1-covid,2-undefined
        for key in self.dictionary[i]:
            how_many_results_temp = [0, 0]
            for result in self.dictionary[i][key]:
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

    def get_report_summary_result(self):
        how_many_results_final = [0,0,0]
        for i in range(len(self.result_list)):
            if(len(self.result_list[i])==0):
                continue
            how_many_result = self.calculate_results(i)
            #if any layer was classified as covid, we classify the patient as covid
            if(how_many_result[1]>0):
                how_many_results_final[1]+=1
            elif(how_many_result[1]==0 and how_many_result[0]==0 and how_many_result[2]>0):
                how_many_results_final[2]+=1
            else:
                how_many_results_final[0]+=1
        return how_many_results_final

    def get_analysis_summary_headers(self):
        res = []
        res.append('Total number of layers')
        res.append('Number of examinations')
        res.append('COVID-19 layers')
        res.append('Normal layers')
        res.append('Uncertain layers')
        return res

    def get_report_summary_headers(self):
        res = []
        res.append('Total number of tests')
        res.append('Tests classified as normal')
        res.append('Tests classified as COVID-19')
        res.append('Uncertain tests')
        return res
    
    def get_report_summary_numbers(self):
        res=[]
        actual_analysis_number = self.get_actual_analysis_total()
        res.append(actual_analysis_number)
        res.extend(self.get_report_summary_result())
        return res
    
    def get_actual_analysis_total(self):
        actual_analysis_number = 0
        for anal in self.result_list:
            if(len(anal)>0):
                actual_analysis_number+=1
        return actual_analysis_number

    def get_analysis_summary_numbers(self,total,analyzed,how_many_results):
        return [total,analyzed,how_many_results[1],how_many_results[0],how_many_results[2]]

    def clear_list(self):
        self.result_list = []