# Main Program file for Cancer Predictive Model
# By: Group 4

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

# Dividing Dataset 70-30
