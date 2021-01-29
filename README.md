# ImagingCOVID-19

Ten folder zawiera pliki źródłowe aplikacji ImagingCOVID-19 bez wytrenowanych modeli ani wykorzystywanych baz danych.

### Wykorzystywane bazy danych 

Do trenowania modeli wykorzystano następujące bazy danych:

1. Modele X-Ray link: https://www.kaggle.com/tawsifurrahman/covid19-radiography-database
> M.E.H. Chowdhury, T. Rahman, A. Khandakar, R. Mazhar, M.A. Kadir, Z.B. Mahbub, K.R. Islam, M.S. Khan, A. Iqbal, N. Al-Emadi, M.B.I. Reaz, M. T. Islam, “Can AI help in screening Viral and COVID-19 pneumonia?” IEEE Access, Vol. 8, 2020, pp. 132665 - 132676.

2. Modele CT link: https://mosmed.ai/datasets/covid19_1110
> Morozov, S.P., Andreychenko, A.E., Pavlov, N.A., Vladzymyrskyy, A.V., Ledikhova, N.V., Gombolevskiy, V.A., Blokhin, I.A.,
Gelezhe, P.B., Gonchar, A.V. and Chernina, V.Y., 2020. MosMedData: Chest CT Scans With COVID-19 Related Findings
Dataset. arXiv preprint arXiv:2005.06465.

### Wykorzystane sieci

1. Sieć klasyfikacji obrazów CT: https://github.com/med-air/Contrastive-COVIDNet
> Wang, Zhao & Liu, Quande & Dou, Qi. (2020). Contrastive Cross-site Learning with Redesigned Net for COVID-19 CT Classification. IEEE journal of biomedical and health informatics. PP. 10.1109/JBHI.2020.3023246. 
2. Sieć segmetnacji płuc z obrazów RTG: https://www.kaggle.com/nikhilpandey360/lung-segmentation-from-chest-x-ray-dataset/notebook

### Ogólna struktura projektu

```
project
│   README.md 
│
└───ImagingCOVID-19
│   └───GUI  
│   │   └───CustomKivyWidgets
│   │   └───main.kv
│   │   └───main.py
│   │   └───sample_image.jpg
│   └───Methods
|   │   └───Train
|   └───tests
|   └───requirements.txt
|   └───instrukcja_uztykownika.pdf
│   
└───models
    └───ct
    └───xray
```

### Wymagania 

Kod napisany jest w języku **python v3.7.1**.

Wymagania dotyczące bibliotek umieszczone są w pliku **requirements.txt**.

### Główny plik

Główny plik **main.py** znajduej się w folderze GUI. 

Program uruchamiany jest komendą *python main.py*

### Modele

Model można wytrenować korzystając ze skryptów w folderze *Train*. Wytrenowane modele należy umieścić w folderze *models*.

Aby wytrenować model, stosujemy następującą logikę:

1. Tworzymy obiekt klasy *ImageEnsemble* dla wybranych obrazów
2. Wywołujemy kolejne metody z klasy *ImageEnsemble*, wykorzystujące klasę *Matrix*, aby otrzymać pożądane cechy (klasy *Matrix*, *Alex* i *Haralick*)
3. Tworzymy obiekt klasy *Model* i dla właściwości odpowiadającej jednemu z czterech modeli wywołujemy metodę *FitModel_typ_klasyfikatora*
4. Serializujemy wytrenowany model za pomocą metody *dump* z biblioteki *joblib*

Aby przetestować model, wykonujemy powyższy schemat, z tą różnicą, że zamiast metody *FitModel_typ_klasyfikatora* wykonujemy metodę *PredictModel_typ_klasyfikatora* używając modelu zdeserializowanego za pomocą funkcji *load* z biblioteki *joblib*.

### Instrukcja użytkownika

Instrukcja została załączona jako plik *instrukcja_uzytkownika.pdf*.
