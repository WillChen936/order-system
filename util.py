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