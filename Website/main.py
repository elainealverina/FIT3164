from flask import Flask, redirect, url_for, render_template, request, session
import os

# Creating a flask app
app = Flask(__name__)
# Specify directory for file upload, file download and file display
directory = os.path.dirname(os.path.abspath(__file__))

app.secret_key = "2021Group4"
# Specify the allowed file type to be submitted by the user
allow_files = {"dcm","jpg","jpeg","tiff","png","tif"}

def delete_files():
    """
    Function that deletes file that is save during the session
    """
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

    target = os.path.join(directory, 'static/upload/')
    if not os.path.isdir(target):
        os.mkdir(target)
    
    # Create folder for file download
    download_dir = os.path.join(directory, 'static/download/')
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
            
    if request.method == "POST":
        # when user submit single images
        if request.form["submit"] == "submit":
            file = request.files["file"]
            filename = file.filename
            
            destination = "/".join([target,filename])
            file.save(destination)
            session["upload_path"] = [destination]
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True) 