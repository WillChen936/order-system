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
    products = util.GetProductList(db_client)
    for key, value in products.items():
        del value["stocks"]
        del value["ordered"]
    
    # Handle the customer's orders
    collection = db_client.db.orders
    cursor = collection.find(
        {"owner": username}
    )
    order = {}
    id = 1
    for doc in cursor:
        goods = doc["goods"]
        order[id] = goods
        id += 1
    return render_template("customer.html", name = username, order = order, products = products)

@app.route("/order", methods = ["POST"])
def Order():
    name = request.form["product"]
    quantity = request.form["quantity"]
    if name == "" or quantity == "":
        return redirect("/error?msg=Please fill in the product or quantity")
    
    # Check the product name and quantity
    collection = db_client.db.products
    product = collection.find_one({
        "name": name
    })
    if not product:
        return redirect("/error?msg=There is no such product")
    if int(product["stocks"]) - int(quantity) < 0:
        msg = "Shortage of stock, stocks: " + product["stocks"]
        return redirect("/error?msg=" + msg)

    # Add product in cart
    if "cart" not in session:
        session["cart"] = {}
    cart = session["cart"]
    if not cart:
        cart = {}
    if cart.get(product["name"]) == None:
        cart[product["name"]] = int(quantity)
    else:
        cart[product["name"]] += int(quantity)
    session["cart"] = cart

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
    products = util.GetProductList(db_client)

    return render_template("manager.html", name = username, products = products)

app.run(port=3000)