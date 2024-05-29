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
    f = open("../datos/arXiv_src_2201_009.jsonl", "r")
    datos = f.readlines()

    for line in datos:
        line_json = json.loads(line)
        id_p = line_json["paper_id"] # extract id field 
        print(line_json["metadata"]["title"])
        # insert pair (id, json) in the db
        collection.insert_one({"_id": id_p, "data": line_json})
    f.close()
# --------------------------------------

def reventar_bd(data_base, collection):
    f = open("../datos/arXiv_src_2201_009.jsonl", "r")
    line = f.readline()
    line_json = json.loads(line)
    for i in range(1,5000):
        collection.insert_one({"_id": i, "data": line_json})
    f.close()
    print("he acabado de reventar ka bd")
    

# -----------------------------------------

def borrar_json (collection):
    collection.delete_many({})
# --------------------------------------

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    borrar_json(collection)
    insertar_json(db, collection)
    #reventar_bd(db, collection) // ha llegado hasta 2600
    #collection.find().sort( [['_id', -1]]).limit(1)
    print("All jsons correctly inserted")
except Exception as e:
    print(e)


