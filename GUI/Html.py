class Html():
    string = None
    def initialize(self):
        self.string = "<!DOCTYPE html><html><head lang="en"><meta charset="UTF-8"></head><body>"

    def close(self):
        self.string+="</body></html>"

    def add_big_title(self,dateStr):
        self.string+="<h4 style=\"text-align:center\">Report generated on "+dateStr+" </h4>"

    def add_small_title(self,title):
        self.string+="<h2 style=\"text-align:center\">"+title+"</h2>"

    def add_table_placeholder(self):
        self.string+="{{table}}"
