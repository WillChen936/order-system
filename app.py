from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://root:root123@ordersystem.m8qeksk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


from flask import Flask

app = Flask(
    __name__,
    static_folder = "public",
    static_url_path="/"
)
app.secret_key = "root123"

@app.route("/")
def index():
    return "Home Page"

app.run()