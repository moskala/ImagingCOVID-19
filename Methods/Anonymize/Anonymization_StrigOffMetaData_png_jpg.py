import os, sys
from PIL import Image 
from pathlib import Path,PurePath

class Anonymize:
    def MetadataStrip(self,image_file):
        if os.path.isfile(image_file):
            directory,filename = os.path.split(image_file)
            image = Image.open(image_file)
            data = list(image.getdata())
            image_without_exif = Image.new(image.mode,image.size)
            image_without_exif.putdata(data)
            newName = os.path.join(directory,"Exif_stripped_"+filename)
            image_without_exif.save(newName)
            print("File saved: newName")
            return newName
        else:
            print("Image path does not exist")
            return ""