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
