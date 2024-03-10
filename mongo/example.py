
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://testAdmin:test@clustertfg.oswjrsi.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTfg"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["test"]
collection = db["test"]

document_id = 1
data = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}

# Insertar el par de datos en la colección
collection.insert_one({"_id": document_id, "data": data})

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)