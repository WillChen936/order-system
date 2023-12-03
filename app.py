from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://root:root123@ordersystem.m8qeksk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


from flask import Flask
from flask import render_template
from flask import redirect
from flask import request

app = Flask(
    __name__,
    static_folder = "public",
    static_url_path="/"
)
app.secret_key = "root123"

@app.route("/")
def Index():
    return render_template("index.html")

@app.route("/login", methods = ["POST"])
def Login():
    username = request.form["username"]
    password = request.form["password"]
    return "Login Page"

@app.route("/signup", methods = ["POST"])
def Signup():
    return "Signup Page"

@app.route("/error")
def Error():
    msg = request.args.get("msg", "There's a error occurred, pls contact with the service dept.")
    return render_template("error.html", message = msg)


app.run(port=3000)