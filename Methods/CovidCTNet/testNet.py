from CovidCTNet.model import CovidNet
import torch
from PIL import Image
from torchvision import transforms
from torch.autograd import Variable
import h5py
import numpy as np
import os


MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'models', 'ct', 'best_checkpoint.pth'))


class Net:
    @staticmethod
    def load_model(path):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        print('Loading model...\n')
        model = CovidNet(bna=True, bnd=True, hidden_size=1024, emmbedding_size=128).to(device)

        model.load_state_dict(
            torch.load(path, map_location=str(device))['state_dict'])
        model.eval()
        return device,model


    @staticmethod
    def predict(img, site, trans,path):
        device,model = Net.load_model(path)
        d = ['normal', 'COVID-19']
        input = trans(img)
        img = input.unsqueeze(0)

        input = Variable(img.to(device))
        score, features = model(input, site)
        probability = torch.nn.functional.softmax(score, dim=1)
        max_value, index = torch.max(probability, 1)

        return d[index.item()], probability, score

    @staticmethod
    def testImage(path):
        modelPath = MODEL_PATH
        site = 'ucsd'
        trans = transforms.Compose([transforms.Resize([224, 224]),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
        img = Image.open(path).convert('RGB')
        pred, prob, score = Net.predict(img, site, trans,modelPath)
        return pred

# testImage(r"C:\Users\Maya\studia\4rok\inz\covidSeg\normal\normal-ct-chest1.jpg")

# testImage(r"C:\Users\Maya\studia\4rok\inz\covidSeg\png\3.jpg")

#C:\Users\Maya\studia\4rok\inz\ai\Contrastive-COVIDNet\data\SARS-Cov-2\non-COVID
# Net.testImage(r"C:\Users\Maya\studia\4rok\inz\ai\Contrastive-COVIDNet\data\SARS-Cov-2\non-COVID\Non-Covid (70).png",r"C:\Users\Maya\studia\4rok\inz\ai\Contrastive-COVIDNet\code\saved\best_checkpoint.pth")

# dataset = ['../data/COVID-CT',
#            '../data/SARS-Cov-2'
#            ]

# dict = {'normal': 0, 'COVID-19': 1}

# for dataset_path in dataset:

#     correct = 0

#     covid_correct = 0
#     covid_predict = 0
#     covid_all = 0

#     files = os.listdir(dataset_path)
#     images = []

#     dirss = os.listdir(dataset_path)

#     dirs = []
#     for a in dirss:
#         if 'txt' in a:
#             continue
#         if 'zip' in a:
#             continue
#         if 'val' in a:
#             continue
#         if 'train' in a:
#             continue
#         if 'test' in a:
#             continue
#         dirs.append(a)

#     testfile = dataset_path + '/test_split.txt'
#     testimages = open(testfile, 'r').readlines()

#     score = torch.from_numpy(np.array([]))
#     target = torch.from_numpy(np.array([]))

#     for input in testimages:
#         # print(input)
#         label = input.split(' ')[-1][:-1]
#         if dataset_path != '../data/COVID-CT':
#             image = input.split(' ')[1] + ' ' + input.split(' ')[2]
#             site = 'new'
#             trans = transforms.Compose(
#                 [transforms.Resize([224, 224]),
#                  transforms.ToTensor(),
#                  transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
#         else:
#             image = '../data/COVID-CT/test/' + input.split(' ')[1]
#             site = 'ucsd'
#             trans = transforms.Compose(
#                 [transforms.Resize([224, 224]),
#                  transforms.ToTensor(),
#                  transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
#         img = Image.open(image).convert('RGB')
#         pred, prob = predict(img, site, trans)
#         if label == pred:
#             correct += 1
#         if label == 'COVID-19':
#             covid_all += 1
#         if pred == 'COVID-19':
#             covid_predict += 1
#         if label == 'COVID-19' and pred == 'COVID-19':
#             covid_correct += 1

#         print(input.split(' ')[1], label, pred, '\t\t', correct, '/', len(testimages))

#     accuracy = float(correct) / float(len(testimages))
#     recall = float(covid_correct) / float(covid_all)
#     precision = float(covid_correct) / float(covid_predict)
#     f1 = 2 * recall * precision / (recall + precision)

#     print(dataset_path[8:], '\tCorrect:', correct, '/', len(testimages),
#           '\nAccuracy:', accuracy, '\tRecall:', recall, '\tPrecision:', precision, '\tF1:', f1)
