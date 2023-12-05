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
        # edit user
        users = self.db.users
        result = users.find_one({
            "username": "Manager"
        })
        if result == None:
            users.insert_one({
                "username": "Manager",
                "password": "123",
                "permission": "admin"
            })
        result = users.find_one({
            "username": "Customer1"
        })
        if result == None:
            users.insert_one({
                "username": "Customer1",
                "password": "123",
                "permission": "visitor"
            })
        result = users.find_one({
            "username": "Customer2"
        })
        if result == None:
            users.insert_one({
                "username": "Customer2",
                "password": "123",
                "permission": "visitor"
            })
