#!/usr/bin/env python
# coding: utf-8

# In[48]:


# https://brainder.org/2012/09/23/the-nifti-file-format/
# https://nipy.org/nibabel/nifti_images.html


# In[49]:


import nibabel
import numpy as np
from pathlib import Path


# In[56]:


def anonymize_and_save_nii(folder_name: str, file_name: str):
    '''
    Funkcja przeprowadza anonimizację na zdjęciach formatu nii. 
    Zbiór 'extra' jest zastępowany pustym zbiorem.
    Funkcja zapisuje zanonimizowane zdjęcie w tym samym folderze.
    Zwraca nowe zdjęcie w formacie nibabel.nifti1.Nifti1Image.
    '''
    
    folder = Path(folder_name)
    img = nibabel.load(folder / file_name)
    
    if img.extra:
        img.extra = {}
        
    anonym_file_name = "anonymized_" + file_name
    save_path = folder / anonym_file_name
    
    nibabel.save(img, save_path)
    
    return img


# In[51]:


# help(img.update_header)
# print(img.header) 


# In[52]:


folder = Path(r"D:\Studia\sem7\inzynierka\data\eksperyment")
file_name = "coronacases_org_001.nii"


# In[57]:


anonymize_nii(folder, file_name)

