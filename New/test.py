import io
import os
import string

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from flask import Flask, flash, request, redirect, url_for, render_template
from PIL import Image
from werkzeug.utils import secure_filename

# Creating a flask app
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load model
model = models.resnet50()
num_inftr = model.fc.in_features
model.fc = nn.Sequential(
    nn.Linear(num_inftr, 256),
    nn.ReLU(),
    nn.Dropout(0.4),
    nn.Linear(256, 10),
    nn.LogSoftmax(dim=1)
)
model.load_state_dict(torch.load('C:/Users/jones/Desktop/FIT3164/New/model.pth',map_location=torch.device('cpu')))
model.eval()

imagenet_class_index = ['MSIMUT', 'MSS']

# Pre-process image
def transform_image(image_bytes):
    my_transforms = transforms.Compose([
		transforms.Resize(256),
		transforms.CenterCrop(224),
		transforms.ToTensor(),
		transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
	])

    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)


def predict(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    out = model.forward(tensor)
    _, index = torch.max(out, 1)
    percentage = nn.functional.softmax(out, dim=1)[0] * 100
    return imagenet_class_index[index], percentage[index[0]].item()


error = "Error"
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template("index.html", error=error)
        file = request.files.get('file')
        if not file:
            return
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_bytes = file.read()
        prediction_name, percentage = predict(img_bytes)
        return render_template("result.html",filename=filename, name = prediction_name, prediction = percentage)
    return render_template('test.html')

@app.route("/about/")
def about():
    """
    Route of about page, display the about page to the user 
    @return: render the about page HTML
    """
    return render_template("about.html")

@app.route("/help/")
def help():
    """
    Route of help page, display the help page to the user 
    @return: render the help page HTML
    """
    return render_template("help.html")

@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run(debug=True)
