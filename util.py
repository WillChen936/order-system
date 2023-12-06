from db import *

class Util:
    def __init__(self, db_client) -> None:
        self.db_client = db_client

    # API for login
    def LogIn(self, username, password):
        collection = self.db_client.db.users
        doc = collection.find_one({
            "$and":[
                {"username": username},
                {"password": password}
            ]
        })
        if not doc:
            return False, "Wrong Username or Password"
        return True, [doc["username"], doc["permission"]]


    # API for orders
    def GetOrderList(self, username, permissions):
        # Handle the customer's orders
        collection = self.db_client.db.orders
        id = 1
        orders = {}
        if permissions == "admin":
            cursor = collection.find()
        else:
            cursor = collection.find(
                {"owner": username}
            )
        for doc in cursor:
            order = {}
            order["owner"] = doc["owner"]
            order["goods"] = doc["goods"]
            orders[id] = order
            id += 1
        return orders
    
    def AddItem(self, name, quantity, cart):
        # Check the product name and quantity
        result, content = self.CheckProductStatus(name, quantity)
        if not result:
            return False, content
        product = content
        # Add new product in cart
        if cart.get(product["name"]) == None:
            cart[product["name"]] = int(quantity)
        else:
            cart[product["name"]] += int(quantity)
        return True, cart
    
    def Order(self, owner, goods, permission): # 檢查權限
        if permission != "visitor":
            return (False, "Permission denied, only customer can create the order.")
        collection = self.db_client.db.products
        # Double check the products name and quantity
        for key, value in goods.items():
            result, content = self.CheckProductStatus(key, value)
        if not result:
            return False, content
        # Minus the quantity in stocks of db and update the ordered status
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
        # Add new order to db
        collection = self.db_client.db.orders
        collection.insert_one({
            "owner": owner,
            "goods": goods
        })
        return True, ""



    # API for products
    def GetProductList(self, permission, filters): # Filter by price or stock
        collection = self.db_client.db.products
        products = {}
        id = 1
        # Define the operator_mapping
        op_map = {}
        op_map[">"] = "$gt"
        op_map[">="] = "$gte"
        op_map["="] = "$eq"
        op_map["<="] = "$lte"
        op_map["="] = "$lt"
        # Filters: [target, judge, number], target will be price or stock.
        # If the filters[0] is empty, that means the other two params are empty.
        if filters[0] == "":
            cursor = collection.find()
        else:
            target, judge, number = filters[0], op_map[filters[1]], int(filters[2])
            cursor = collection.find({
                target: {judge: number}
            })
        for doc in cursor:
            product = {}
            product["name"] = doc["name"]
            product["price"] = doc["price"]
            product["stocks"] = doc["stocks"]
            if permission == "admin":
                product["ordered"] = doc["ordered"]
            products[id] = product
            id += 1 
        return products
    
    def CheckProductStatus(self, name, quantity):
        collection = self.db_client.db.products
        product = collection.find_one({
            "name": name
        })
        if not product:
            return False, "There is no such product"
        if product["stocks"] - quantity < 0:
            return False, "Shortage of stock, stocks: " + str(product["stocks"])
        return True, product
    
    def ProductCreate(self, name, price, stocks, permission):
        if permission != "admin":
            return (False, "Permission denied, only admin can manage the product info.")
        collection = self.db_client.db.products
        collection.insert_one({
            "name": name,
            "price": float(price),
            "stocks": int(stocks),
            "ordered": False
        })

    def ProductEdit(self,  name, price, stocks, permission):
        if permission != "admin":
            return (False, "Permission denied, only admin can manage the product info.")
        collection = self.db_client.db.products
        product = collection.find_one({ "name": name })
        if not product:
            return False
        collection.update_one({
            "name": name
        }, {
            "$set": {
                "price": float(price),
                "stocks": int(stocks)
            }
        })
        return True
    
    def ProductDelete(self, name, permission):
        if permission != "admin":
            return (False, "Permission denied, only admin can manage the product info.")
        collection = self.db_client.db.products
        product = collection.find_one({ "name": name })
        if not product:
            return (False, "There is no such product")
        if product["ordered"] == True:
            return (False, "The product is ordered, couldn't be deleted")
        collection.delete_one({
            "name": name
        })
        return (True, "")