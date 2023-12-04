from pymongo.mongo_client import MongoClient

class DBClient:
    def __init__(self) -> None:
        uri = "mongodb+srv://root:root123@ordersystem.m8qeksk.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(uri)
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        self.db = self.client.order_system

        collection_user = self.db.user
        result = collection_user.find_one({
            "username": "Manager"
        })
        if result == None:
            collection_user.insert_one({
                "username": "Manager",
                "password": "123",
                "permission": "admin"
            })
        result = collection_user.find_one({
            "username": "Customer1"
        })
        if result == None:
            collection_user.insert_one({
                "username": "Customer1",
                "password": "123",
                "permission": "visitor"
            })