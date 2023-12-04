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
        
        # Edit Product
        products = self.db.products
        result = products.find_one({
            "name": "Product1"
        })
        if result == None:
            products.insert_many([{
                "name": "Product1",
                "price": "30.2",
                "stock": "15",
                "ordered": "False"
            }, {
                "name": "Product2",
                "price": "40.2",
                "stock": "7",
                "ordered": "False"
            }, {
                "name": "Product3",
                "price": "13.2",
                "stock": "20",
                "ordered": "False"
            }])

        # Edit Order
        orders = self.db.orders
        result = orders.find_one({
            "id": "1"
        })
        if result == None:
            orders.insert_one({
                "id": "1",
                "owner": "Customer1",
                "products": [{"Product1": "4"}, {"Product3": "2"}]
            })
