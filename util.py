from db import *

class Util:
    # API for orders
    def GetOrderList(self, db_client, username, permissions):
        # Handle the customer's orders
        collection = db_client.db.orders
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
    
    def AddItem(self, db_client, name, quantity, cart):
        # Check the product name and quantity
        result, content = self.CheckProductStatus(db_client, name, quantity)
        if not result:
            return False, content
        product = content
        # Add new product in cart
        if cart.get(product["name"]) == None:
            cart[product["name"]] = int(quantity)
        else:
            cart[product["name"]] += int(quantity)
        return True, cart
    
    def Order(self, db_client, owner, goods):
        collection = db_client.db.products
        # Double check the products name and quantity
        for key, value in goods.items():
            result, content = self.CheckProductStatus(db_client, key, value)
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
        collection = db_client.db.orders
        collection.insert_one({
            "owner": owner,
            "goods": goods
        })
        return True, ""



    # API for products
    def GetProductList(self, db_client, permission):
        collection = db_client.db.products
        products = {}
        id = 1
        for doc in collection.find():
            product = {}
            product["name"] = doc["name"]
            product["price"] = doc["price"]
            if permission == "admin":
                product["stocks"] = doc["stocks"]
                product["ordered"] = doc["ordered"]
            products[id] = product
            id += 1
        return products
    
    def CheckProductStatus(self, db_client, name, quantity):
        collection = db_client.db.products
        product = collection.find_one({
            "name": name
        })
        if not product:
            return False, "There is no such product"
        if product["stocks"] - quantity < 0:
            return False, "Shortage of stock, stocks: " + str(product["stocks"])
        return True, product
    
    def ProductCreate(self, db_client, name, price, stocks):
        collection = db_client.db.products
        collection.insert_one({
            "name": name,
            "price": float(price),
            "stocks": int(stocks),
            "ordered": False
        })

    def ProductEdit(self, db_client, name, price, stocks):
        collection = db_client.db.products
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
    
    def ProductDelete(self, db_client, name):
        collection = db_client.db.products
        product = collection.find_one({ "name": name })
        if not product:
            return (False, "There is no such product")
        if product["ordered"] == True:
            return (False, "The product is ordered, couldn't be deleted")
        collection.delete_one({
            "name": name
        })
        return (True, "")