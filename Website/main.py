from flask import Flask, redirect, url_for, render_template, request, session, flash
import os
#from loadmodel import load_model
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
# Creating a flask app
app = Flask(__name__)
# Specify directory for file upload, file download and file display
directory = os.path.dirname(os.path.abspath(__file__))

app.secret_key = "2021Group4"
# Specify the allowed file type to be submitted by the user
accept_files = {"jpg","jpeg","png"}

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

    def __init__(self, first_name, email, password):
        self.email = email
        self.password = password
        self.first_name = first_name


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
    return render_template("index.html")

@app.route("/about/", methods = ['GET', 'POST'])
def about():
    return render_template("about.html")

@app.route("/help/", methods = ['GET', 'POST'])
def help():
    return render_template("help.html")

@app.route("/signup/", methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First Name must be greater than 1 character', category='error')
        elif password1 != password2:
            flash('Password not matched', category='error')
        elif len(password1) < 7:
            flash('Password is too short', category='error')
        else:
            new_user = User(email=email, first_name=firstName, password=generate_password_hash(password1, method='sha256'))            
            db.session.add(new_user)
            db.session.commit()
            flash("Account created !", category='success')

    return render_template("signup.html")

@app.route("/login/", methods = ['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route("/view/")
def view():
    return render_template("view.html", values = User.query.all())

@app.route("/logout/", methods = ['GET', 'POST'])
def logout():
    return "<p>Logout</p>"

@app.route("/result/", methods = ['GET', 'POST'])
def result():
    result_list = []
    image = session["uploads"]
    #specify session to delete files later
    session["upload_path"] = []
    session["download"] = []

    temp = ""
    for ele in image:
        temp += ele

    file_path = "static/upload/"+ temp
    #get the type of image ( png , jpg and etc)
    file_type = temp.rsplit(".", 1)[1].lower()
    #the name of the image
    file_prefix = temp.rsplit(".", 1)[0]
    print(file_prefix)
    session["upload_path"].append(file_path)

    new_file_name = file_prefix + ".png"
    result_list.append([new_file_name])

    # uploaded image by users are variable named temp 
    # code of prediction model go here #
    # images uploaded by users are saved under static/upload #
    # read the image inside the folder and run through the prediction model #
    # then display the result in result.html #
    return render_template("result.html",images_name = result_list)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True) 