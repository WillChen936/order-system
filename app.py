from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from db import*

app = Flask(
    __name__,
    static_folder = "public",
    static_url_path="/"
)

Database = DB()

app.secret_key = "root123"

@app.route("/")
def Index():
    return render_template("index.html")

@app.route("/login", methods = ["POST"])
def Login():
    username = request.form["username"]
    password = request.form["password"]

    if username == "" or password == "":
        return redirect("/error?msg=Please fill in the username or password")
    
    doc = collection_user.find_one({
        "$and":[
            {"username": username},
            {"password": password}
        ]
    })
    if not doc:
        return redirect("/error?msg=Username or Password is wrong")
    
    if username == "Manager":
        return redirect("/manager")
    else:
        return redirect("/customer?name=" + username)
    

@app.route("/signup", methods = ["POST"])
def Signup():
    username = request.form["username"]
    password = request.form["password"]

    if username == "" or password == "":
        return redirect("/error?msg=Please fill in the username or password")
    
    return "Signup Page"

@app.route("/error")
def Error():
    msg = request.args.get("msg", "There's a error occurred, pls contact with the service dept.")
    return render_template("error.html", message = msg)

@app.route("/manager")
def Manager():
    username = request.args.get("name", "")
    return render_template("manager.html", name = username)

@app.route("/customer")
def Customer():
    username = request.args.get("name", "")
    return render_template("customer.html", name = username)


app.run(port=3000)