#http://localhost:5601/
from opensearchpy import OpenSearch
from opensearch_dsl import Search
from opensearch_dsl import Document, Text, Keyword
import json


def insertar_json(client, index_name, json_file):
    # Abre el archivo JSONL
    with open(json_file, "r") as f:
        datos = f.readlines()

        # Itera sobre cada línea del archivo JSONL
        for line in datos:
            # Carga el JSON de la línea actual
            line_json = json.loads(line)
            id_p = line_json["paper_id"] # Extrae el campo "paper_id"

            # Inserta el documento en OpenSearch
            client.index(index=index_name, body=line_json)

    print("Data inserted successfully.")




host = 'localhost'
port = 9200
auth = ('admin', 'admin') # For testing only. Don't store credentials in code.
ca_certs_path = '/full/path/to/root-ca.pem' # Provide a CA bundle if you use intermediate CAs with your root CA.

# Create the client with SSL/TLS enabled, but hostname verification disabled.
client = OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = auth,
    use_ssl = True,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False,
    ca_certs = ca_certs_path
)



# index_name = 'my-dsl-index2'
# index_body = {
#   'settings': {
#     'index': {
#       'number_of_shards': 4
#     }
#   }
# }

# response = client.indices.create(index_name, body=index_body)

# class Movie(Document):
#     title = Text(fields={'raw': Keyword()})
#     director = Text()
#     year = Text()

#     class Index:
#         name = index_name

#     def save(self, ** kwargs):
#         return super(Movie, self).save(** kwargs)

# # Set up the opensearch-py version of the document
# Movie.init(using=client)
# doc = Movie(meta={'id': 1}, title='Moneyball', director='Bennett Miller', year='2011')
# response = doc.save(using=client)



# s = Search(using=client, index="my-dsl-index2") \
#     .filter("term", year="2011") \
#     .query("match", title="Moneyball")

# response = s.execute()


# Perform a search query to check if there are any documents
# response = client.search(index="my-dsl-index2", body={"query": {"match_all": {}}})

# # Obtén los documentos de la respuesta
# hits = response["hits"]["hits"]

# # Imprime los documentos recuperados
# if hits:
#     print("Documents in the index:")
#     for hit in hits:
#         print(hit["_source"])
# else:
#     print("There are no documents in the index.")


index_name = "49jsons"
# new_settings = {
#     "index.mapping.total_fields.limit": 20000  # Define el nuevo límite de campos totales
# }

# Actualiza la configuración del índice
#client.indices.put_settings(index=index_name, body=new_settings)

#print(f"Updated total fields limit for index '{index_name}'.")
#json_file = "../datos/un_json.jsonl"
#insertar_json(client, index_name, json_file)

#Perform a search query to check if there are any documents
response = client.search(index=index_name, body={"query": {"match_all": {}}})

# imprimir el numero total de documentos en ese indice
hits = response["hits"]["hits"]
num_documents = len(hits)
print(f"Number of documents in the index: {num_documents}")
if hits:
    print("First field and its value of each document:")
    for hit in hits:
        source = hit["_source"]
        first_field = next(iter(source.items()))
        print(f"{first_field[0]}: {first_field[1]}")
else:
    print("There are no documents in the index.")

index_settings = client.indices.get_settings(index=index_name)

# Obtiene el número total de campos presentes en la configuración del índice
total_campos = index_settings[index_name]["settings"]["index"]["mapping"]["total_fields"]["limit"]

print(f"Total de campos almacenados en el índice '{index_name}': {total_campos}")


# Imprime los documentos recuperados
# if hits:
#     print("Documents in the index:")
#     for hit in hits:
#         print(hit["_source"])
# else:
#     print("There are no documents in the index.")




