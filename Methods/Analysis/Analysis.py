

class Analysis():
    result_list = None
    dictionary = None
    slices_number = None
    def __init__(self,slices_number,lst=None):
        if(lst is None):
            self.result_list = []
        else:
            self.result_list = lst
        self.dictionary = {}
        self.slices_number = slices_number
    
    def add_to_list(self,result):
        self.result_list.append(result)

    def get_dictionary_by_method_from_list(self):
        dictionary_method = {}
        for result in self.result_list:
            method = result.get_method_name()+","+str(result.get_object_ct_window())
            if(dictionary_method.keys().__contains__(method)):
                dictionary_method[method].append(result)
            else:
                temp_list = [result]
                dictionary_method.update({method:temp_list})
        return dictionary_method   

    def get_analysis_summary_headers(self):
        res = []
        res.append('Total number of layers')
        res.append('Number of analyzed layers')
        res.append('COVID-19 layers')
        res.append('Normal layers')
        res.append('Uncertain layers')
        return res
    
    def get_analysis_summary_numbers(self,total,analyzed,how_many_results):
        return [total,analyzed,how_many_results[1],how_many_results[0],how_many_results[2]]

    def clear_list(self):
        self.result_list = []