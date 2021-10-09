from flask import Flask, redirect, url_for, render_template, request, session, flash, request
import os
import pickle

#from loadmodel import load_model
from PIL import Image


import torch
import torch.nn as nn

from torchvision import transforms
from torchvision.transforms import transforms

# Creating a flask app
app = Flask(__name__)




# Load model
model = torch.load('best_model.pth',map_location=torch.device('cpu'))
model.eval()

imagenet_class_index = ['MSIMUT_JPEG', 'MSS_JPEG']

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
    return percentage[index[0]].item()


# Specify directory for file upload, file download and file display
directory = os.path.dirname(os.path.abspath(__file__))

app.secret_key = "2021Group4"
# Specify the allowed file type to be submitted by the user
accept_files = {"jpg","jpeg","png"}


def file_checker(file):
    """
    Take in a input called file and return T/F to show which file to accept
    @param file: user submitted file
    @return: True / False
    """
    return "." in file and file.rsplit(".", 1)[1].lower() in accept_files

def delete_files():
    """
    Delete files that saved during the session
    """
    if 'upload_path' in session:
        for path in session['upload_path']:
            os.remove(path)   
        
    if 'download' in session:
        for path in session['download']:
            os.remove(path)

@app.route("/", methods = ['GET','POST'])
def home():
    """
    Route of homepage, display the homepage to the user and listen to GET and POST
    Add user submitted image to a file
    @return: render the homepage HTML
    """
    image_list = []
    #will delete files when user go to main home page
    delete_files()
    session.clear()

    # Create folder for file upload
    upload_dir = os.path.join(directory, 'static/upload/')
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)
    
    # Create folder for file download
    download_dir = os.path.join(directory, 'static/download/')
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
    
    error = None


    if request.method == "POST":        
        # when user submit image
        if request.form["submit"] == "submit":

            file = request.files["file"]
            filename = file.filename

            if filename == "":
                error = "File is empty"
                return render_template("index.html", error=error)
            
            if file_checker(filename) == False:
                error = "This file is not accepted"
                return render_template("index.html", error=error)


            destination = "/".join([upload_dir,filename])
            file.save(destination)
            session["upload_path"] = [destination]
            image_list.append(filename)
        
        
    session["uploads"] = image_list
    return render_template("test.html")

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


@app.route("/view/")
def view():
    """
    Route of view, display the view page to the user
    display all user authentication details except password
    @return: render the view HTML page
    """
    return render_template("view.html", values = User.query.all())


@app.route("/result/", methods = ['GET', 'POST'])
def result():
    """
    Route for user to analysis their medical image
    run predictive model on user submitted image
    @return: render the result HTML page
    """
    result_list = []
    image = session["uploads"]
    #specify session to delete files later
    session["upload_path"] = []
    session["download"] = []

    temp = ""
    for ele in image:
        temp += ele

    file_path = "static/upload/"+ temp

    #get the type of image (png , jpg and etc)
    file_type = temp.rsplit(".", 1)[1].lower()
    
    #the name of the image
    file_prefix = temp.rsplit(".", 1)[0]
    session["upload_path"].append(file_path)

    new_file_name = file_prefix + ".jpg"
    #put result into result_list, for now is user submitted image
    result_list.append([new_file_name])

    # uploaded image by users are variable named temp 
    # images uploaded by users are saved under static/upload #

    # read the image inside the folder and run through the prediction model #
    image = Image.open(file_path)
    print(predict(image))
    temp1 = predict(image)

    # then display the result in result.html #
    return render_template("result.html",images_name = result_list, prediction = predict(image))


if __name__ == "__main__":
    app.run(debug=True) 
