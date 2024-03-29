# http://localhost:5601/
# buscar en todos los archivos del directorio actual: grep -nr "texto" .


from opensearchpy import OpenSearch
from opensearch_dsl import Search
from opensearch_dsl import Document, Text, Keyword
import os
import json
import time 




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


def deserializar(linea):
    return json.loads(linea)



def insertar_carpeta(carpeta, client, index_name):
    files = [f for f in os.listdir(carpeta)]
    start_time = time.time()
    insertados = 0
    print(carpeta)
    for f in files:
        print(f)
        nombre = carpeta + f 
        print(str(nombre))
        insertados += insertar_json_serializado(client, index_name, nombre)
    print("--- %s seconds ---" % (time.time() - start_time))
    print("--- %d insertados ---" % (insertados))
    

def insertar_json_serializado(client, index_name, json_file):
    # Abre el archivo JSONL
    with open(json_file, "r") as f:
        datos = f.readlines()
        # Itera sobre cada línea del archivo JSONL
        i = 0
        for line in datos:
            # Carga el JSON de la línea actual
            line_json = json.loads(line)
            # Extrae el campo "paper_id"
            id_p = line_json["paper_id"]
            # Serializa el JSON completo
            documento_serializado = json.dumps(line_json)
            # Crea un nuevo documento con el JSON completo serializado
            documento = {
                "paper_id": id_p,  # Se incluye el paper_id
                "json_data": documento_serializado  # Se incluye el JSON completo serializado
            }
            # Inserta el documento en OpenSearch
            client.index(index=index_name, body=documento)
            i = i + 1
            print("i: " + str(i))
    print("Data inserted successfully.")
    return i


def obtener_numero_campos_ocupados(client, index_name):
    """
    Obtiene el número de campos ocupados en un índice.

    Args:
        client: Cliente de OpenSearch.
        index_name: Nombre del índice del cual se quiere obtener el número de campos ocupados.
    
    Returns:
        El número de campos ocupados en el índice.
    """
    # Obtener el mapping del índice
    mapping = client.indices.get_mapping(index=index_name)

    # Contar el número de campos en el mapping
    numero_campos_ocupados = len(mapping[index_name]["mappings"]["properties"])

    return numero_campos_ocupados


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
    resultado = client.search(index=index_name, body={"query": {"term": {"paper_id": paper_id}}}, _source=["json_data"])
    hits = resultado["hits"]["hits"]
    # Verifica si hay resultados
    if hits:
        for hit in hits:
            print(hit["_source"]["json_data"])  # Imprime el contenido de json_data
    else:
        print(f"No se encontró ningún documento con el paper_id '{paper_id}' en el índice '{index_name}'.")






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

def eliminar_documentos_indice(client, index_name):
    query_delete = {
        "query": {
            "match_all": {}
        }
    }
    response = client.delete_by_query(index=index_name, body=query_delete)
    # Verificar si la operación fue exitosa
    if response["deleted"] > 0:
        print(f"Se han eliminado {response['deleted']} documentos del índice {index_name}.")
    else:
        print(f"No se eliminaron documentos del índice {index_name}.")


#--------------------------------------------------------
def eliminar_indice(client, index_name):
    #Nombre del índice que deseas eliminar

    #Verificar si el índice existe antes de intentar eliminarlo
    if client.indices.exists(index=index_name):
        # Eliminar el índice
        client.indices.delete(index=index_name)
        print(f"Se ha eliminado el índice '{index_name}'.")
    else:
        print(f"El índice '{index_name}' no existe.")



def verificar_insercion_json_data(client, index_name, paper_id):
    # Realiza una búsqueda utilizando el paper_id como filtro
    resultado = client.search(index=index_name, body={"query": {"term": {"paper_id": paper_id}}})

    # Verifica si se encontraron documentos
    hits = resultado["hits"]["hits"]
    if hits:
        # El primer hit contiene el documento encontrado
        documento_encontrado = hits[0]["_source"]
        # Verifica si el campo 'json_data' está presente en el documento
        if "json_data" in documento_encontrado:
            #print("Contenido de 'json_data':", documento_encontrado["json_data"])
            print("encontrado")
            return True
    return False


def imprimir_documentos_de_indice(client, index_name):
    # Realiza una búsqueda para obtener todos los documentos del índice
    resultado = client.search(index=index_name, body={"query": {"match_all": {}}})
    hits = resultado["hits"]["hits"]

    # Verifica si se encontraron documentos
    if hits:
        # Itera sobre los documentos e imprime los campos "paper_id" y "json_data"
        for hit in hits:
            documento = hit["_source"]
            print("Documento ID:", hit["_id"])
            print("paper_id:", documento.get("paper_id"))
            json_data = documento.get("json_data")
            if json_data is not None:
                #print("json_data:", json_data)
                print("encontrado")
            else:
                print("json_data: Campo no presente en el documento")
            print()  # Línea en blanco para separar los documentos
    else:
        print(f"No se encontraron documentos en el índice '{index_name}'.")



###################################################
def main1():
    client = conexion()
    index_name = "carpeta_08"
    eliminar_indice(client, index_name)
    response = crear_indice(index_name, client)
    print(str(response))
    insertar_carpeta("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/unarXive_230324_open_subset/08/", client, index_name)
    #insertar_json(client, "prueba_i_1", "../datos/un_json.jsonl")
    #eliminar_documentos_indice(client, "indice_serializado")
    #insertar_json_serializado(client, index_name, "../datos/un_json.jsonl")
    verificado = verificar_insercion_json_data(client, index_name, "0801.4603")
    if verificado:
        print("El campo 'json_data' se ha insertado correctamente.")
    else:
        print("El campo 'json_data' no se ha insertado correctamente.")
    #imprimir_documentos_de_indice(client, index_name)
    
###################################################
def main2():
    files = insertar_carpeta("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/unarXive_230324_open_subset/21/")
    print(str(files))
    
###################################################
def main_info():
    client = conexion()
    index_name = "carpeta_08"
    #obtener_documento_por_paper_id(client, index_name, "0801.3099") 
    campos = obtener_campos_de_indice(client, index_name)
    print("Campos del índice:", campos)
    
###################################################

def main_eliminar():
    client = conexion()
    eliminar_indice(client, "prueba_i_1")
    eliminar_indice(client, "my-dsl-index")
    eliminar_indice(client, "indice_serializado")
    eliminar_indice(client, "carpeta_07")
    eliminar_indice(client, "solo")

###################################################

main_eliminar()


