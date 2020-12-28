# https://www.kaggle.com/nikhilpandey360/lung-segmentation-from-chest-x-ray-dataset/output
from keras.models import *
from keras.layers import *
import numpy as np
import cv2
from pathlib import Path
import sys
sys.path.append(str(Path().resolve().parent))
from Grayscale import get_grayscale_from_jpg_png

MODEL_WEIGHTS = str(Path().resolve().parent.parent.parent / "models" / "cxr_reg_weights.best.hdf5")


def unet(input_size=(256, 256, 1)):
    """
    Creates model architecture
    :param input_size:
    :return:
    """
    inputs = Input(input_size)

    conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(pool1)
    conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = Conv2D(128, (3, 3), activation='relu', padding='same')(pool2)
    conv3 = Conv2D(128, (3, 3), activation='relu', padding='same')(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

    conv4 = Conv2D(256, (3, 3), activation='relu', padding='same')(pool3)
    conv4 = Conv2D(256, (3, 3), activation='relu', padding='same')(conv4)
    pool4 = MaxPooling2D(pool_size=(2, 2))(conv4)

    conv5 = Conv2D(512, (3, 3), activation='relu', padding='same')(pool4)
    conv5 = Conv2D(512, (3, 3), activation='relu', padding='same')(conv5)

    up6 = concatenate([Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(conv5), conv4], axis=3)
    conv6 = Conv2D(256, (3, 3), activation='relu', padding='same')(up6)
    conv6 = Conv2D(256, (3, 3), activation='relu', padding='same')(conv6)

    up7 = concatenate([Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(conv6), conv3], axis=3)
    conv7 = Conv2D(128, (3, 3), activation='relu', padding='same')(up7)
    conv7 = Conv2D(128, (3, 3), activation='relu', padding='same')(conv7)

    up8 = concatenate([Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(conv7), conv2], axis=3)
    conv8 = Conv2D(64, (3, 3), activation='relu', padding='same')(up8)
    conv8 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv8)

    up9 = concatenate([Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same')(conv8), conv1], axis=3)
    conv9 = Conv2D(32, (3, 3), activation='relu', padding='same')(up9)
    conv9 = Conv2D(32, (3, 3), activation='relu', padding='same')(conv9)

    conv10 = Conv2D(1, (1, 1), activation='sigmoid')(conv9)

    return Model(inputs=[inputs], outputs=[conv10])


def prepare_model(dim=512):
    model = unet(input_size=(dim, dim, 1))
    model.load_weights(MODEL_WEIGHTS)
    return model


def predict_single_lung_mask(image_name, image_folder, dim=512):
    img = get_grayscale_from_jpg_png(image_name, image_folder)
    resized = cv2.resize(img, (dim, dim))
    reshaped = np.array(resized).reshape(dim, dim, 1)
    model = prepare_model(512)
    prediction = model.predict(np.array([reshaped]))
    return np.squeeze(prediction)

def predict_multiple_lung_mask(images_names, images_folder, dim=512):
    images = [get_grayscale_from_jpg_png(name, images_folder) for name in images_names]
    resized = [cv2.resize(img, (dim, dim)) for img in images]
    reshaped = [np.array(img).reshape(dim, dim, 1) for img in resized]
    model = prepare_model(512)
    # model.predict(reshaped) - można, ale wywaliło kernel - TODO przetestować!

    predictions = [model.predict(np.array([img])) for img in reshaped]
    return [np.squeeze(pred) for pred in predictions]


#Testowanie
import os
folder_name = r"D:\Studia\sem7\inzynierka\data\COVID-19 Radiography Database"
covid_folder = Path(folder_name) / "COVID-19"
normal_folder = Path(folder_name) / "NORMAL"

covid = os.listdir(covid_folder)
normal = os.listdir(normal_folder)

image = get_grayscale_from_jpg_png(normal[10], str(normal_folder))
mask = predict_single_lung_mask(normal[10], str(normal_folder))

from LungSegmentationUtilities import compare_plots

# compare_plots(image, mask)
compare_plots(image, mask*cv2.resize(image, (512, 512)))