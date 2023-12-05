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
