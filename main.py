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
## input_folder: coad_msi_mss
def img_train_test_split(input_folder, output_folder):
    """
    This function splits a folder with subfolders into train and test datasets
    :param input_folder: a string: file path of the folder of subfolders of images
    :param output_folder: a string: path to the output folder
    :return: -
    """
    splitfolders.ratio(input_folder, output_folder, seed=0, ratio=(.7, .3))
    return None