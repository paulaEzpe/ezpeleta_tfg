#http://localhost:5601/
from opensearchpy import OpenSearch
from opensearch_dsl import Search
from opensearch_dsl import Document, Text, Keyword
import json

def conexion():
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
    return client



def insertar_json(client, index_name, json_file):
    # Abre el archivo JSONL
    with open(json_file, "r") as f:
        datos = f.readlines()

        # Itera sobre cada línea del archivo JSONL
        for line in datos:
            # Carga el JSON de la línea actual
            line_json = json.loads(line)
            id_p = line_json["paper_id"] # Extrae el campo "paper_id"

            # Crea un nuevo documento con solo el campo "paper_id"
            documento = {
                "paper_id": id_p
            }
            # Inserta el documento en OpenSearch
            client.index(index=index_name, body=documento)

    print("Data inserted successfully.")


def obtener_paper_id_indice(indice, client):
    # Realiza una consulta de búsqueda para verificar si hay algún documento
    response = client.search(index=indice, body={"query": {"match_all": {}}})
    # Verifica si hay documentos en el índice
    hits = response["hits"]["hits"]
    if hits:
        # Obtiene el paper_id del primer documento
        source = hits[0]["_source"]
        paper_id = source.get("paper_id")
        if paper_id:
            return paper_id
        else:
            return None
    else:
        return None



def obtener_documento_por_paper_id(client, index_name, paper_id):
    # Realiza una búsqueda utilizando el paper_id como filtro
    resultado = client.search(index=index_name, body={"query": {"term": {"paper_id": paper_id}}})

    # Verifica si hay resultados
    if resultado["hits"]["total"]["value"] > 0:
        # Obtiene el primer documento (en caso de que haya múltiples resultados)
        documento = resultado["hits"]["hits"][0]["_source"]
        # Imprime el cuerpo completo del documento
        print(json.dumps(documento, indent=2))
    else:
        print(f"No se encontró ningún documento con el paper_id '{paper_id}' en el índice '{index_name}'.")

    # Ejemplo de uso
    obtener_documento_por_paper_id(client, "nombre_del_indice", "paper_id_a_buscar")    





def crear_indice(indice, client):
    index_name = indice
    index_body = {
        'settings': {
            'index': {
            'number_of_shards': 4
            }
        }
    }
    response = client.indices.create(index_name, body=index_body)
    print("Se ha creado el índice")
    return response




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

# new_settings = {
#     "index.mapping.total_fields.limit": 20000  # Define el nuevo límite de campos totales
# }

# Actualiza la configuración del índice
#client.indices.put_settings(index=index_name, body=new_settings)

#print(f"Updated total fields limit for index '{index_name}'.")
#json_file = "../datos/un_json.jsonl"
#insertar_json(client, index_name, json_file)




def imprimir_numdoc_indice(indice, client):
    #Perform a search query to check if there are any documents
    response = client.search(index=indice, body={"query": {"match_all": {}}})
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

    index_settings = client.indices.get_settings(index=indice)

#----------------------------------------------------------------------

# Obtiene el número total de campos presentes en la configuración del índice
# total_campos = index_settings[index_name]["settings"]["index"]["mapping"]["total_fields"]["limit"]
# print(f"Total de campos almacenados en el índice '{index_name}': {total_campos}")

#-------------------------------------------------------------------------


#IMPRIMIR TODOS DOCUMENTOS DE INDICE
# Imprime los documentos recuperados
# if hits:
#     print("Documents in the index:")
#     for hit in hits:
#         print(hit["_source"])
# else:
#     print("There are no documents in the index.")



#----------------------------------------------------------------------------
# eliminar todos los documentos del indice:

# query_delete = {
#     "query": {
#         "match_all": {}
#     }
# }
# response = client.delete_by_query(index=index_name, body=query_delete)
# # Verificar si la operación fue exitosa
# if response["deleted"] > 0:
#     print(f"Se han eliminado {response['deleted']} documentos del índice {index_name}.")
# else:
#     print(f"No se eliminaron documentos del índice {index_name}.")


#--------------------------------------------------------
def eliminar_indice(index_name):
    #Nombre del índice que deseas eliminar

    #Verificar si el índice existe antes de intentar eliminarlo
    if client.indices.exists(index=index_name):
        # Eliminar el índice
        client.indices.delete(index=index_name)
        print(f"Se ha eliminado el índice '{index_name}'.")
    else:
        print(f"El índice '{index_name}' no existe.")


###################################################3

client = conexion()
#response = crear_indice("prueba_i_1", client)
#print(str(response))
insertar_json(client, "prueba_i_1", "../datos/un_json.jsonl")
imprimir_numdoc_indice("prueba_i_1", client)
papel = obtener_paper_id_indice("prueba_i_1", client)
obtener_documento_por_paper_id(client, "prueba_i_1", papel)


