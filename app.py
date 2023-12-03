from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://root:root123@ordersystem.m8qeksk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client.order_system
collection_user = db.user
result = collection_user.find_one({
    "username": "Manager"
})
if result == None:
    collection_user.insert_one({
        "username": "Manager",
        "password": "manager123",
        "permission": "admin"
    })


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
        return redirect("/customer")
    

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
    return render_template("manager.html")

@app.route("/customer")
def Customer():
    return render_template("customer.html")


app.run(port=3000)