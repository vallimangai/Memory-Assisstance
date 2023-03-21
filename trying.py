from tensorflow import keras
from flask import Flask, render_template, session, request, url_for, redirect
from flask.helpers import make_response
from flask.json import jsonify
from werkzeug.utils import secure_filename
from bson.json_util import dumps
from datetime import date
import cv2
import pymongo
import json
from bson import ObjectId
# import trying as fs
from flask import *
from PIL import Image
import io
import face_siamese as fs
reconstructed_model = keras.models.load_model("my_model.h5")
print(reconstructed_model.summary())




myclient = pymongo.MongoClient("mongodb://localhost:27017/")
myDB = myclient["Tarps"]


users = myDB["users"]
relatives=myDB["relatives"]
todos=myDB["todo"]
diary=myDB["diary"]
album=myDB["album"]

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


app = Flask(__name__)
app.secret_key = "abcdevalli"

@app.route("/")
def home():
    if "email" in session:
        return render_template("Home.html")
    else:
        return redirect(url_for("login"))
@app.route("/Home")
def home1():
    if "email" in session:
        return render_template("Home.html")
    else:
        return redirect(url_for("login"))
@app. route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["passwd"]

        # check credentials
        x = users.find_one({'email': user_email})
        if x is not None:
            if x['password'] == user_password:
                session["email"] = user_email
                return redirect(url_for("home"))
            else:
                return render_template("login.html", message="Wrong password")
        else:
            return render_template("login.html", message="Invalid email id")

    else:
        return render_template("login.html", message="")
@app. route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user_email = request.form.get("email")
        user_name = request.form.get("usrname")
        user_password = request.form.get("passwd")
        file = request.files.get("file")
        im = Image.open(file)

        image_bytes = io.BytesIO()
        im.save(image_bytes, format='JPEG')
        if users.count_documents({'email': user_email}) == 0:
            new_user = {
                'email': user_email,
                'username': user_name,
                'password': user_password,
                'image':image_bytes.getvalue()
            }
            users.insert_one(new_user)
            session["email"] = user_email
            return redirect(url_for("home"))
        else:
            return render_template(
                "login.html", message="User account already exists")
    else:
        return render_template("signup.html")
@app. route("/logout", methods=["GET"])
def logout():
    session.pop('email', None)
    return redirect(url_for("home"))


@app.route("/addface")
def add():
    if(session.get("email") != None):
        return  render_template("addface.html")
    else:
        return  redirect("/login")
@app.route("/face_reg")
def face():
    if(session.get('email') != None):
        return render_template("rec_face.html")
    else:
        return redirect("/login")

@app.route("/face_recogni",methods=['POST','GET'])
def face_rec():
    if(session.get('email') != None):
        img1 = request.files.get('img')
        img1.save("img1.png")
        image = relatives.find({'email':session.get('email')})
        a=[]
        name="unkown"
        score=0.5
        relation="Unkown"
        for img2 in image:
            print(img2["_id"])
            pil_img = Image.open(io.BytesIO(img2['image']))
            pil_img.save("img2.png")
            s=fs.check_sim("img1.png","img2.png")
            if(s>score):
                score=s
                name=img2["name"]
                relation=img2["relative"]
        print(image)
        return name+" "+relation
    else:
        return redirect("/login")
@app.route("/addingface", methods=["POST", "GET"])
def adding_face():
    if(session.get('email') != None):
        name = request.form.get("name",False)
        relative = request.form.get("relation",False)
        file = request.files.get('img')
        print(type(file))
        im = Image.open(file)
        image_bytes = io.BytesIO()
        im.save(image_bytes, format='JPEG')
        new_rela = {
                'email': session.get('email'),
                'name': name,
                'relative': relative,
                'image': image_bytes.getvalue()
            }
        relatives.insert_one(new_rela)
        return "Added successfully"
    else:
        return redirect("/login")


@app.route("/whac")
def whac():
    return render_template("whac.html")
@app.route("/memory")
def memory():
    return render_template("memory.html")

@app.route("/todo",methods=["POST","GET"])
def todo():
    if request.method=="POST":
        print(date.today())
        content = request.form["content"]
        dat = date.today()
        email = session.get("email")
        tod = {
            "content": content,
            "date": str(dat),
            "email": email
        }
        todos.insert_one(tod)
        return  redirect('/todo')
    else:
        ta = list(todos.find({'email': session.get('email')}))
        print(len(ta))
        return render_template('todo.html', tasks=ta)
@app.route('/delete/<string:id>')
def delete(id):
    task_to_delete=todos.find({"_id":id})
    print(task_to_delete)
    todos.delete_many({"_id": ObjectId(id)})
    return redirect('/todo')
@app.route("/diary")
def diary1():
    today = date.today()
    if "email" in session:
        ta = list(diary.find({'email': session.get('email')}))
        print(len(ta))
        return render_template("diary.html",entry=ta)
    else:
        return redirect(url_for("login"))

@app.route("/add_diary",methods=["POST","GET"])
def diaryentry():
    today = date.today()
    if "email" in session:
        if request.method == "POST":
            print(date.today())
            title=request.form["name"]
            content = request.form["entry"]
            dat = date.today()

            email = session.get("email")
            dia = {
                "date": str(dat),
                "email": email,
                "title":title,
                "content": content
            }
            diary.insert_one(dia)
            return redirect(url_for("diary1"))
        else:
            return render_template("add_diary.html")
    else:
        return redirect(url_for("login"))

@app.route('/read/<string:id>',methods=["POST","GET"])
def read(id):
    e=list(diary.find({"_id":ObjectId(id)}))
    print({"_id":"ObjectId('"+id+"')"},e)
    return render_template('entry.html',e=e[0])



@app.route("/uploadmemory",methods=["POST","GET"])
def uploadmemory():
    if "email" in session:
        if request.method == "POST":
            file = request.files.get('img')
            msg = request.form.get("msg", False)
            print(type(file))
            im = Image.open(file)
            img = im.resize((300,300))
            image_bytes = io.BytesIO()
            img.save(image_bytes, format='JPEG')
            new_rela = {
                'email': session.get('email'),
                'msg':msg,
                'image': image_bytes.getvalue()
            }
            album.insert_one(new_rela)
            return "Added successfully"
        else:
            return render_template("upload_memory.html")
    else:
        return redirect(url_for("login"))
@app.route("/displaymemory")
def displaymemory():

    image = album.find({'email': session.get('email')})
    a = []
    i=0
    for img2 in image:
        print(img2["_id"])
        pil_img = Image.open(io.BytesIO(img2['image']))
        pil_img.save("static/cdn/img"+str(i)+".png")
        a.append({"msg":img2["msg"],"path":"img"+str(i)+".png"})
        i=i+1
    print(a)
    return render_template("display_memory.html",paths=a)
if __name__ == "__main__":
    app.run(debug=True)