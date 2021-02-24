import torch
from PIL import Image
from torchvision import transforms
from torch.autograd import Variable
import h5py
import numpy as np
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model import CovidNet

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
        return device, model

    @staticmethod
    def predict(img, site, trans, path):
        device, model = Net.load_model(path)
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
        pred, prob, score = Net.predict(img, site, trans, modelPath)
        return pred
