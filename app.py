from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import session
from db import *
from util import *

# Init the program
app = Flask(
    __name__,
    static_folder = "public",
    static_url_path="/"
)
app.secret_key = "root123"
# Build DB instance
db_client = DBClient()
util = Util()

# Build routes
@app.route("/")
def Index():
    return render_template("index.html")

@app.route("/login", methods = ["POST"])
def Login():
    session.clear()
    username = request.form["username"]
    password = request.form["password"]
    collection = db_client.db.users
    if username == "" or password == "":
        return redirect("/error?msg=Please fill in the username or password")
    
    doc = collection.find_one({
        "$and":[
            {"username": username},
            {"password": password}
        ]
    })
    if not doc:
        return redirect("/error?msg=Username or Password is wrong")
    
    # Save the user status
    session["user"] = username
    session["permission"] = doc["permission"]
    if username == "Manager":
        return redirect("/manager?name=" + username)
    else:
        return redirect("/customer?name=" + username)
    
@app.route("/logout")
def Logout():
    session.clear()
    return redirect("/")


@app.route("/error")
def Error():
    msg = request.args.get("msg", "There's a error occurred, pls contact with the service dept.")
    return render_template("error.html", message = msg)

# Function implement for customer
# Inlcuding take an order and carts design
@app.route("/customer")
def Customer():
    # Prevent from directly access by url & get username
    if "user" not in session:
        return redirect("/")
    username = request.args.get("name", "")
    # Handle the product list, costomer shouldn't see stocks & ordered
    products = util.GetProductList(db_client, session["permission"])
    # Handle the order list, costomer should see only it's own order
    orders = util.GetOrderList(db_client, session["user"], session["permission"])
    return render_template("customer.html", name = username, orders = orders, products = products)

@app.route("/order", methods = ["POST"])
def Order():
    name = request.form["product"]
    quantity = request.form["quantity"]
    # Check the form
    if name == "" or quantity == "":
        return redirect("/error?msg=Please fill in the product or quantity") 
    # Add new product in cart
    if "cart" not in session:
        session["cart"] = {}
    result, content = util.TakeOrder(db_client, name, int(quantity), session["cart"])
    if result:
        session["cart"] = content
    else:
        return redirect("/error?msg=" + content)
    return redirect("/cart")

@app.route("/cart")
def Cart():
    list = session["cart"]
    return render_template("cart.html", cart = list)

@app.route("/send_order")
def SendOrder():
    goods = session["cart"]   
    owner = session["user"]

    # minus the stocks in db
    collection = db_client.db.products
    for key, value in goods.items():
        collection.update_one({
            "name": key
        }, {
            "$inc": {
                "stocks" : -value
            }
        })
        collection.update_one({
            "name": key
        }, {
            "$set": {
                "ordered" : True
            }
        })

    collection = db_client.db.orders
    collection.insert_one({
        "owner": owner,
        "goods": goods
    })
    del session["cart"]

    return redirect("/customer?name=" + session["user"])


# Function implement for manager
# Inlcuding CRUD for db.products
@app.route("/manager")
def Manager():
    # Prevent from directly access by url & get username
    if "user" not in session:
        return redirect("/")
    username = request.args.get("name", "")
    # Handle the product list
    products = util.GetProductList(db_client, session["permission"])
    # Handle the order list, costomer should see only it's own order
    orders = util.GetOrderList(db_client, session["user"], session["permission"])
    return render_template("manager.html", name = username, orders = orders, products = products)

@app.route("/product_create", methods = ["POST"])
def ProductCreate():
    name = request.form["name"]
    price = request.form["price"]
    stocks = request.form["stocks"]
    util.ProductCreate(db_client, name, price, stocks)
    return redirect("/manager?name=" + session["user"])

@app.route("/product_edit", methods = ["POST"])
def ProductEdit():
    name = request.form["name"]
    price = request.form["price"]
    stocks = request.form["stocks"]
    result = util.ProductEdit(db_client, name, price, stocks)
    if not result:
        return redirect("/error?msg=There is no such product")
    return redirect("/manager?name=" + session["user"])

@app.route("/product_delete", methods = ["POST"])
def ProductDelete():
    name = request.form["name"]
    result, msg = util.ProductDelete(db_client, name)
    if not result:
        return redirect("/error?msg=" + msg)
    return redirect("/manager?name=" + session["user"])

app.run(port=3000)