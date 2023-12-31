from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import session
from db import *
from util import *

# Init the server
app = Flask(
    __name__,
    static_folder = "public",
    static_url_path="/"
)
app.secret_key = "root123"
# Build DB instance
db_client = DBClient()
util = Util(db_client)


# Build routes
@app.route("/")
def Index():
    return render_template("index.html")


# Function implement for Login & Logout
@app.route("/login", methods = ["POST"])
def Login():
    # clear the seesion before login
    session.clear()
    username = request.form["username"]
    password = request.form["password"]
    if username == "" or password == "":
            return redirect("/error?msg=Please fill in the username or password")
    # Login process
    result, content = util.LogIn(username, password)
    if not result:
        return redirect("/error?msg=" + content)
    # Save the user status
    session["user"] = content[0]
    session["permission"] = content[1]
    if session["permission"] == "admin":
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


# Handle the Product List
@app.route("/product_list", methods = ["POST"])
def ProductList():
    # Handle the product list, costomer shouldn't see the status "ordered".
    target = request.form["target"]
    judge = request.form["judge"]
    number = request.form["number"]
    # Implement XNOR, all empty means you want to see the whole list, without filter.
    result = (target == "" and judge == "" and number == "") or (target != "" and judge != "" and number != "")
    if not result:
        return redirect("/error?msg=Filters should be all filled in or empty.")
    filters = [target, judge, number]
    products = util.GetProductList(session["permission"], filters)
    return render_template("product_list.html", products = products)


# Function implement for customer
# Inlcuding take an order and shooping cart design
@app.route("/customer")
def Customer():
    # Prevent from directly access by url.
    if "user" not in session:
        return redirect("/")
    username = request.args.get("name", "")
    # Handle the order list, costomer should see only it's own order
    orders = util.GetOrderList(session["user"], session["permission"])
    return render_template("customer.html", name = username, orders = orders)

@app.route("/add_item", methods = ["POST"])
def AddItem():
    name = request.form["product"]
    quantity = request.form["quantity"]
    # Check the form
    if name == "" or quantity == "":
        return redirect("/error?msg=Please fill in the product or quantity") 
    # Add new product in cart, use session to save the shopping cart status.
    if "cart" not in session:
        session["cart"] = {}
    result, content = util.AddItem(name, int(quantity), session["cart"])
    if result:
        session["cart"] = content
    else:
        return redirect("/error?msg=" + content)
    return redirect("/cart")

@app.route("/cart")
def Cart():
    cart = session["cart"]
    name = session["user"]
    return render_template("cart.html", cart = cart, name = name)

@app.route("/back")
def Back():
    return redirect("/customer?name=" + session["user"])

@app.route("/order")
def Order():
    goods = session["cart"]   
    owner = session["user"]
    result, content = util.Order(owner, goods, session["permission"])
    if not result:
        return redirect("/error?msg=" + content)
    del session["cart"]
    return redirect("/customer?name=" + session["user"])


# Function implement for manager
# Inlcuding CRUD for db.products
@app.route("/manager")
def Manager():
    # Prevent from directly access by url.
    if "user" not in session:
        return redirect("/")
    username = request.args.get("name", "")
    # Handle the order list, manager can see all orders.
    orders = util.GetOrderList(session["user"], session["permission"])
    return render_template("manager.html", name = username, orders = orders)

@app.route("/product_create", methods = ["POST"])
def ProductCreate():
    name = request.form["name"]
    price = request.form["price"]
    stock = request.form["stock"]
    if name == "" or price == "" or stock == "":
        return redirect("/error?msg=Please fill in the name, price and stock")
    util.ProductCreate(name, price, stock, session["permission"])
    return redirect("/manager?name=" + session["user"])

@app.route("/product_edit", methods = ["POST"])
def ProductEdit():
    name = request.form["name"]
    price = request.form["price"]
    stock = request.form["stock"]
    if name == "" or price == "" or stock == "":
        return redirect("/error?msg=Please fill in the name, price and stock")
    result = util.ProductEdit(name, price, stock, session["permission"])
    if not result:
        return redirect("/error?msg=There is no such product")
    return redirect("/manager?name=" + session["user"])

@app.route("/product_delete", methods = ["POST"])
def ProductDelete():
    name = request.form["name"]
    if name == "":
        return redirect("/error?msg=Please fill in the name")
    result, msg = util.ProductDelete(name, session["permission"])
    if not result:
        return redirect("/error?msg=" + msg)
    return redirect("/manager?name=" + session["user"])


# Server run
app.run(port=3000)