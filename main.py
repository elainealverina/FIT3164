# Main Program file for Cancer Predictive Model
# By: Group CL_04

# Libraries
import numpy as np
import matplotlib.pyplot as plt
import time
import os, random, shutil
import copy

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision
from torchvision import *
from torch.utils.data import Dataset, DataLoader

import splitfolders


# Dividing Dataset 70-30
# ## input_folder: coad_msi_mss
# def img_train_test_split(input_folder, output_folder):
#     """
#     This function splits a folder with subfolders into train and test datasets
#     :param input_folder: a string: file path of the folder of subfolders of images
#     :param output_folder: a string: path to the output folder
#     :return: -
#     """
#     splitfolders.ratio(input_folder, output_folder, seed=0, ratio=(.7, .3))
#     return None

def img_train_test_split(root_dir, classes_dir, test_ratio):
    '''
    This function splits a folder with subfolders into train and test datasets
    :param root_dir: a string corresponding to the file path of the folder of subfolders of images
    :param classes_dir: a list of strings of subfolder names
    :param test_ratio: a float of the ratio of test dataset to train dataset
    :return: None
    '''

    for cls in classes_dir:
        # create a new train and test directory for cls
        os.makedirs(root_dir + 'train/' + cls)
        os.makedirs(root_dir + 'test/' + cls)

        # get pathname of cls
        src = root_dir + cls

        # split the filenames into chosen training and testing ratio
        allFileNames = os.listdir(src)
        np.random.shuffle(allFileNames)
        train_FileNames, test_FileNames = np.split(np.array(allFileNames),
                                                   [int(len(allFileNames) * (1 - test_ratio))])

        # copy images into new train folder for cls subfolder
        for name in train_FileNames:
            shutil.copy(root_dir + cls + '/' + name, root_dir + 'train/' + cls)

        # copy images into new test folder for cls subfolder
        for name in test_FileNames:
            shutil.copy(root_dir + cls + '/' + name, root_dir + 'test/' + cls)
    return None


# root_dir: filepath of coad_msi_mss with '/' at the back
root_dir = '/Users/vionnietan/Desktop/trial_dataset/'
# root_dir = '/Users/elainealverina/Desktop/trial_dataset/'
classes_dir = ['MSIMUT_JPEG', 'MSS_JPEG']
test_ratio = 0.3

img_train_test_split(root_dir, classes_dir, test_ratio)


# Data Augmentation and Normalization
# batch_size = 128
learn_rate = 1e-3

data_transformation_train = transforms.Compose([transforms.RandomHorizontalFlip(), transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
data_transformation_test = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

train_image_dataset = datasets.ImageFolder(root_dir, transform=data_transformation_train)
test_image_dataset = datasets.ImageFolder(root_dir, transform=data_transformation_test)

# Prepare DataLoader
train_image_dataloader = DataLoader(train_image_dataset, batch_size=128, shuffle=True)
test_image_dataloader = DataLoader(test_image_dataset, batch_size=128, shuffle=True)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Data Visualization (Display some images)

def show_image(images, title=None):
    plt.figure(figsize=(8,4))
    for i, image in enumerate(images):
        #plt.subplot(1, 2, i + 1, xticks=[], yticks=[])
        image = image.cpu() if device else image
        image = image.numpy().transpose((1, 2, 0))

        # Denormalize image
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image = std * image + mean
        image = np.clip(image, 0, 1)
        plt.imshow(image)

    plt.show()


images, labels = next(iter(train_image_dataloader))
#out = torchvision.utils.make_grid(images)
show_image(images)

# Creating the Model - Load resnet18

# Training Model
