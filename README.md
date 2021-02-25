# ImagingCOVID-19

ImagingCOVID-19 is desktop application for computer-aided recognition of COVID-19 in chest imaging. The program supports the analysis of uploaded files and generating feedback on the results obtained from recognizing COVID-19 symptoms on the analyzed images. It was created as a student project at Warsaw Universty of Technology.

COVID-19 is a contagious respiratory disease, caused by becoming infected with SARS-CoV-2 virus, which high infection rate caused 2020 global pandemic. Many COVID-19 patients develop respiratory symptoms, with lung lesions made visible by X-Ray or CT images. 

This app contains the following functionalities for CT and X-Ray images:

* Anonymization of medical images
* Vizualization for formats DICOM, NIfTI, JPEG, PNG
* Lungs segmentation
* Features extraction from grayscale images
* Features classification 
* Selection the study layers for analysis
* Manual selection COVID-19 lung lesions and calculating severity score
* Generating reports based on the obtained results


### Databases

1. X-Ray images: https://www.kaggle.com/tawsifurrahman/covid19-radiography-database
> M.E.H. Chowdhury, T. Rahman, A. Khandakar, R. Mazhar, M.A. Kadir, Z.B. Mahbub, K.R. Islam, M.S. Khan, A. Iqbal, N. Al-Emadi, M.B.I. Reaz, M. T. Islam, “Can AI help in screening Viral and COVID-19 pneumonia?” IEEE Access, Vol. 8, 2020, pp. 132665 - 132676.

2. CT images: https://mosmed.ai/datasets/covid19_1110
> Morozov, S.P., Andreychenko, A.E., Pavlov, N.A., Vladzymyrskyy, A.V., Ledikhova, N.V., Gombolevskiy, V.A., Blokhin, I.A.,
Gelezhe, P.B., Gonchar, A.V. and Chernina, V.Y., 2020. MosMedData: Chest CT Scans With COVID-19 Related Findings
Dataset. arXiv preprint arXiv:2005.06465.

### Neural networks

1. Classification of CT images: https://github.com/med-air/Contrastive-COVIDNet
> Wang, Zhao & Liu, Quande & Dou, Qi. (2020). Contrastive Cross-site Learning with Redesigned Net for COVID-19 CT Classification. IEEE journal of biomedical and health informatics. PP. 10.1109/JBHI.2020.3023246. 
2. Segmentation lungs from X-Ray images: https://www.kaggle.com/nikhilpandey360/lung-segmentation-from-chest-x-ray-dataset/notebook

### Project structure

```
project
└───ImagingCOVID-19
│   └───GUI  
│   │   └───main.kv
│   │   └───main.py
│   └───Methods
|   │   └───Train
|   └───tests
└───models
    └───ct
    └───xray
```

### Requirements 

Application is implemented in **python v3.7.1** and **Kivy** framework. 
All required libraries are listed in the file **requirements.txt**.

### Start

To start application run **main.py** script.
