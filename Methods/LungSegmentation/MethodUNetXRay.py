# https://www.kaggle.com/nikhilpandey360/lung-segmentation-from-chest-x-ray-dataset/output

from keras.models import *
from keras.layers import *
import numpy as np
import cv2
from pathlib import Path
import scipy.ndimage as ndimage
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Grayscale import get_grayscale_from_jpg_png
from LungSegmentation.LungSegmentationUtilities import fill_contours

MODEL_WEIGHTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'models', 'xray', "cxr_reg_weights.best.hdf5"))
INPUT_DIMENSION = 512


def unet(input_size=(256, 256, 1)):
    """Creates model architecture"""
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


def prepare_model(dim=INPUT_DIMENSION, model_weights_path=MODEL_WEIGHTS):
    """Loads model weights from given path"""
    model = unet(input_size=(dim, dim, 1))
    model.load_weights(model_weights_path)
    return model


def predict_single_lung_mask(image_name, image_folder, dim=INPUT_DIMENSION, model_weights_path=MODEL_WEIGHTS):
    """Predicts single lungmask for image in given folder"""
    img = get_grayscale_from_jpg_png(image_name, image_folder)
    resized = cv2.resize(img, (dim, dim))
    reshaped = np.array(resized).reshape(dim, dim, 1)
    model = prepare_model(dim, model_weights_path)
    prediction = model.predict(np.array([reshaped]))
    return np.squeeze(prediction)


def predict_multiple_lung_mask(images_names, images_folder, dim=INPUT_DIMENSION, model_weights_path=MODEL_WEIGHTS):
    """Predicts multiple lungmasks for images in given folder"""
    images = [get_grayscale_from_jpg_png(name, images_folder) for name in images_names]
    resized = [cv2.resize(img, (dim, dim)) for img in images]
    reshaped = [np.array(img).reshape(dim, dim, 1) for img in resized]
    model = prepare_model(dim, model_weights_path)
    predictions = model.predict(np.array(reshaped))  
    return [np.squeeze(pred) for pred in predictions]


def predict_single_lung_mask_from_array(grayscale_image, dim=INPUT_DIMENSION, model_weights_path=MODEL_WEIGHTS):
    """Predicts single lungmask for given image"""
    resized = cv2.resize(grayscale_image, (dim, dim))
    reshaped = np.array(resized).reshape(dim, dim, 1)
    model = prepare_model(dim, model_weights_path)
    prediction = model.predict(np.array([reshaped]))
    return np.squeeze(prediction)


def predict_multiple_lung_mask_from_array(grayscale_images, dim=INPUT_DIMENSION, model_weights_path=MODEL_WEIGHTS):
    """Predicts multiple lungmasks for given images"""
    resized = [cv2.resize(img, (dim, dim)) for img in grayscale_images]
    reshaped = [np.array(img).reshape(dim, dim, 1) for img in resized]
    model = prepare_model(dim, model_weights_path)
    predictions = model.predict(np.array(reshaped))  
    return [np.squeeze(pred) for pred in predictions]


def adjust_mask(mask):
    """Convert mask to binary array and smooth contours"""
    mask = np.where(mask > 0.1, 1, 0)
    mask = fill_contours(mask, min_length=100)
    mask = ndimage.gaussian_filter(mask, sigma=0.2)
    return mask


def prepare_image_to_segmentation(image):
    """Prepare image to segmentation by size and normalization"""
    img = image.copy()
    if np.max(img) <= 1:
        img *= 255
    img = img.astype(np.uint8)
    equ = cv2.equalizeHist(img)
    return equ / 255


def make_lungmask(filename, folder, model_weights_path=MODEL_WEIGHTS):
    """Make single lungmask for image in given folder"""
    image = get_grayscale_from_jpg_png(filename, folder)
    img_to_process = prepare_image_to_segmentation(image)
    mask = predict_single_lung_mask_from_array(img_to_process, model_weights_path=model_weights_path)
    mask = adjust_mask(mask)
    segment = mask * cv2.resize(image, (INPUT_DIMENSION, INPUT_DIMENSION))
    return segment, mask


def make_lungmask_multiple(filenames, folder, model_weights_path=MODEL_WEIGHTS):
    """Makes multiple lungmasks for images in given folder"""
    images = [get_grayscale_from_jpg_png(filename, folder) for filename in filenames]
    img_to_process = [prepare_image_to_segmentation(image) for image in images]
    masks = predict_multiple_lung_mask_from_array(img_to_process, model_weights_path=model_weights_path)
    masks = [adjust_mask(mask) for mask in masks]
    segments = [mask * cv2.resize(image, (INPUT_DIMENSION, INPUT_DIMENSION)) for image, mask in zip(images, masks)]
    return segments, masks
