from db import *

class Util:
    def GetProductList(self, db_client):
        # Handle the product list
        collection = db_client.db.products
        products = {}
        id = 1
        for doc in collection.find():
            product = {}
            product["name"] = doc["name"]
            product["price"] = doc["price"]
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
