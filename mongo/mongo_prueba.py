import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi



uri = "mongodb+srv://testAdmin:test@clustertfg.oswjrsi.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTfg"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["test"]
collection = db["test"]


# --------------------------------------
def insertar_json (data_base, collection):
    f = open("../datos/arXiv_src_2212_086.jsonl", "r")
    datos = f.readlines()

    for line in datos:
        line_json = json.loads(line)
        id_p = line_json["paper_id"] # extract id field 
        print(line_json["metadata"]["title"])
        # insert pair (id, json) in the db
        collection.insert_one({"_id": id_p, "data": line_json})
    f.close()
# --------------------------------------

def borrar_json (collection):
    collection.delete_many({})
# --------------------------------------

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    # borrar_json(collection)
    insertar_json(db, collection)
    print("All jsons correctly inserted")
except Exception as e:
    print(e)



# Send a ping to confirm a successful connection
