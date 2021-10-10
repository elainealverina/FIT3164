from flask import Flask, render_template, request, session
import pickle 

from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.transforms import transforms

# Creating a flask app
app = Flask(__name__)

# Load model
model = pickle.load(open('finalized_model.pkl','rb'))
model.eval()

imagenet_class_index = ['MSIMUT', 'MSS']

# Pre-process image
def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    img_preprocess = my_transforms(image_bytes)
    return torch.unsqueeze(img_preprocess,0)

def predict(image):
    image = transform_image(image)
    out = model(image)
    _, index = torch.max(out, 1)
    percentage = nn.functional.softmax(out, dim=1)[0] * 100
    print(percentage[index[0]].item(), index)
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
		img_bytes = Image.open(file)
		prediction_name, percentage = predict(img_bytes)
		return render_template("result.html",name = prediction_name, prediction = percentage)
    
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

if __name__ == "__main__":
    app.run(debug=True) 
