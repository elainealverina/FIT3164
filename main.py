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
root_dir = ''
classes_dir = ['MSIMUT_JPEG', 'MSS_JPEG']
test_ratio = 0.3

img_train_test_split(root_dir,classes_dir,test_ratio)

# Data Augmentation and Normalization