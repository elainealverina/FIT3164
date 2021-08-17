from flask import Flask, redirect, url_for, render_template, request, session
import os
#from loadmodel import load_model
from PIL import Image


# Creating a flask app
app = Flask(__name__)
# Specify directory for file upload, file download and file display
directory = os.path.dirname(os.path.abspath(__file__))

app.secret_key = "2021Group4"
# Specify the allowed file type to be submitted by the user
accept_files = {"jpg","jpeg","png"}

def file_checker(file):
    return "." in file and file.rsplit(".", 1)[1].lower() in accept_files


def delete_files():
    if 'upload_path' in session:
        for path in session['upload_path']:
            os.remove(path)   
        
    if 'download' in session:
        for path in session['download']:
            os.remove(path)

@app.route("/", methods = ['GET','POST'])
def home():

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

    return render_template("index.html")

@app.route("/about/", methods = ['GET', 'POST'])
def about():

    return render_template("about.html")

@app.route("/help/", methods = ['GET', 'POST'])
def help():

    return render_template("help.html")


@app.route("/result/", methods = ['GET', 'POST'])
def result():
    # code of prediction model go here #
    # images uploaded by users are saved under static/upload #
    # read the image inside the folder and run through the prediction model #
    # then display the result in result.html #

    return render_template("result.html")

if __name__ == "__main__":
    app.run(debug=True) 