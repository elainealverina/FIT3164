from flask import Flask, redirect, url_for, render_template, request, session, flash, request
import os
import pickle

#from loadmodel import load_model
from PIL import Image
from flask_login import login_manager, login_user, login_required, logout_user, current_user, LoginManager
from flask_login.mixins import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import torch
import torch.nn as nn

from torchvision import transforms
from torchvision.transforms import transforms

# Creating a flask app
app = Flask(__name__)

# Database Environment
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/lexus'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ivfhdyrrndcrfn:3826cbe8f164c64724fdb82e6f82da023dcd09e49e87b8f4abe68fbbb6df01ad@ec2-52-206-193-199.compute-1.amazonaws.com:5432/d7gmviuqv6dfph'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# load model
model = pickle.load(open('finalized_model.pkl','rb'))
#model = torch.load('/Users/vionnietan/Desktop/FIT3163 - FIT3164/FIT3164/FIT3164/Website/resnet18.pth')
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

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#Database model for user authentication system
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    vCancer = db.Column(db.String(150))
    vSymptoms = db.Column(db.String(150))
    vTreatment = db.Column(db.String(150))
    result = db.Column(db.String(150))


    def __init__(self, first_name, email, password, vCancer, vSymptoms, vTreatment, result):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.vCancer = vCancer
        self.vSymptoms = vSymptoms
        self.vTreatment = vTreatment
        self.result = result
        

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
            vCancer = request.form.get('vCancer')
            vSymptoms = request.form.get('vSymptoms')
            vTreatment = request.form.get('vTreatment')

            file = request.files["file"]
            filename = file.filename

            if filename == "":
                error = "File is empty"
                return render_template("index.html", error=error)
            
            if file_checker(filename) == False:
                error = "This file is not accepted"
                return render_template("index.html", error=error)

            if current_user.is_authenticated:
                update_user = User.query.filter_by(email= current_user.email).first()
                update_user.vCancer = vCancer
                update_user.vSymptoms = vSymptoms
                update_user.vTreatment = vTreatment
                db.session.commit()


            destination = "/".join([upload_dir,filename])
            file.save(destination)
            session["upload_path"] = [destination]
            image_list.append(filename)
        
        
    session["uploads"] = image_list
    return render_template("index.html", user = current_user)

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

@app.route("/signup/", methods = ['GET', 'POST'])
def signup():
    """
    Route of signup, display the signup page to the user and listen to GET and POST
    Added data submitted by users into database
    @return: render the signup HTML page
    """
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email = email).first()
        if user:
            flash('Email already exists.', category= 'error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First Name must be greater than 1 character', category='error')
        elif password1 != password2:
            flash('Password not matched', category='error')
        elif len(password1) < 7:
            flash('Password is too short', category='error')
        else:
            new_user = User(email=email, first_name=firstName, password=generate_password_hash(password1, method='sha256'), vCancer= "", vSymptoms="",vTreatment="",result ="")            
            db.session.add(new_user)
            db.session.commit()
            flash("Account created !", category='success')
            return redirect(url_for("login"))


    return render_template("signup.html", user = current_user)

@app.route("/login/", methods = ['GET', 'POST'])
def login():
    """
    Route of login, display the login page to the user and listen to GET and POST
    check user authentication when login
    @return: render the login HTML page
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category = 'success')
                login_user(user, remember = True)
                return redirect(url_for("home"))
            else:
                flash('Incorrect password.', category= 'error')
        else:
            flash('Email does not exist.', category = 'error')

    return render_template("login.html", user = current_user)

@app.route("/view/")
def view():
    """
    Route of view, display the view page to the user
    display all user authentication details except password
    @return: render the view HTML page
    """
    return render_template("view.html", values = User.query.all())

@app.route("/logout/", methods = ['GET', 'POST'])
@login_required
def logout():
    """
    Route for user to logout 
    @return: redirect to login HTML page
    """
    logout_user()
    return redirect(url_for("login"))

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
    #file_path = "/Users/vionnietan/Desktop/trial_dataset/coad_msi_mss/MSIMUT_JPEG/"+ temp
    # file_path = '/Users/vionnietan/Desktop/FIT3163 - FIT3164/FIT3164/FIT3164/Website/static/upload/' + temp
    #file_path = '/Users/elainealverina/Desktop/trial_dataset/MSIMUT_JPEG/' + temp


    #get the type of image ( png , jpg and etc)
    file_type = temp.rsplit(".", 1)[1].lower()
    
    #the name of the image
    file_prefix = temp.rsplit(".", 1)[0]
    session["upload_path"].append(file_path)

    new_file_name = file_prefix + ".jpg"
    #put result into result_list, for now is user submitted image
    result_list.append([new_file_name])

    # uploaded image by users are variable named temp 
    # code of prediction model go here #
    # images uploaded by users are saved under static/upload #

    # read the image inside the folder and run through the prediction model #
    image = Image.open(file_path)
    print(predict(image))
    temp1 = predict(image)

    if current_user.is_authenticated:
        update_user = User.query.filter_by(email= current_user.email).first()
        update_user.result = temp1
        db.session.commit()


    # then display the result in result.html #
    return render_template("result.html",images_name = result_list, prediction = predict(image))



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True) 
