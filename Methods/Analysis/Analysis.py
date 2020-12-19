

class Analysis():
    result_list = None
    def __init__(self,lst=None):
        if(lst is None):
            self.result_list = []
        else:
            self.result_list = lst
    def add_to_list(self,result):
        self.result_list.append(result)

    def clear_list(self):
        self.result_list = []