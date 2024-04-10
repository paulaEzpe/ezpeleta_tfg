"""
Nombre del archivo: high_client.py
Autora: Paula Ezpeleta Castrillo
Fecha de creación: 24/03/2024
Descripción: Archivo que contiene el código necesario para todas las operaciones con OpenSearch

"""

# http://localhost:5601/
# buscar en todos los archivos del directorio actual: grep -nr "texto" .
#username y passwd: admin



from opensearchpy import OpenSearch
from opensearch_dsl import Search
from opensearch_dsl import Document, Text, Keyword
import os
import json
import time 
import re

latexAccents = [
  [ u"à", "\\`a" ], # Grave accent
  [ u"è", "\\`e" ],
  [ u"ì", "\\`\\i" ],
  [ u"ò", "\\`o" ],
  [ u"ù", "\\`u" ],
  [ u"ỳ", "\\`y" ],
  [ u"À", "\\`A" ],
  [ u"È", "\\`E" ],
  [ u"Ì", "\\`\\I" ],
  [ u"Ò", "\\`O" ],
  [ u"Ù", "\\`U" ],
  [ u"Ỳ", "\\`Y" ],
  [ u"á", "\\'a" ], # Acute accent
  [ u"é", "\\'e" ],
  [ u"í", "\\'\\i" ],
  [ u"ó", "\\'o" ],
  [ u"ú", "\\'u" ],
  [ u"ý", "\\'y" ],
  [ u"Á", "\\'A" ],
  [ u"É", "\\'E" ],
  [ u"Í", "\\'\\I" ],
  [ u"Ó", "\\'O" ],
  [ u"Ú", "\\'U" ],
  [ u"Ý", "\\'Y" ],
  [ u"â", "\\^a" ], # Circumflex
  [ u"ê", "\\^e" ],
  [ u"î", "\\^\\i" ],
  [ u"ô", "\\^o" ],
  [ u"û", "\\^u" ],
  [ u"ŷ", "\\^y" ],
  [ u"Â", "\\^A" ],
  [ u"Ê", "\\^E" ],
  [ u"Î", "\\^\\I" ],
  [ u"Ô", "\\^O" ],
  [ u"Û", "\\^U" ],
  [ u"Ŷ", "\\^Y" ],
  [ u"ä", "\\\"a" ],    # Umlaut or dieresis
  [ u"ë", "\\\"e" ],
  [ u"ï", "\\\"\\i" ],
  [ u"ö", "\\\"o" ],
  [ u"ü", "\\\"u" ],
  [ u"ÿ", "\\\"y" ],
  [ u"Ä", "\\\"A" ],
  [ u"Ë", "\\\"E" ],
  [ u"Ï", "\\\"\\I" ],
  [ u"Ö", "\\\"O" ],
  [ u"Ü", "\\\"U" ],
  [ u"Ÿ", "\\\"Y" ],
  [ u"ç", "\\c{c}" ],   # Cedilla
  [ u"Ç", "\\c{C}" ],
  [ u"œ", "{\\oe}" ],   # Ligatures
  [ u"Œ", "{\\OE}" ],
  [ u"æ", "{\\ae}" ],
  [ u"Æ", "{\\AE}" ],
  [ u"å", "{\\aa}" ],
  [ u"Å", "{\\AA}" ],
  [ u"–", "--" ],   # Dashes
  [ u"—", "---" ],
  [ u"ø", "{\\o}" ],    # Misc latin-1 letters
  [ u"Ø", "{\\O}" ],
  [ u"ß", "{\\ss}" ],
  [ u"¡", "{!`}" ],
  [ u"¿", "{?`}" ],
  [ u"\\", "\\\\" ],    # Characters that should be quoted
  [ u"~", "\\~" ],
  [ u"&", "\\&" ],
  [ u"$", "\\$" ],
  [ u"{", "\\{" ],
  [ u"}", "\\}" ],
  [ u"%", "\\%" ],
  [ u"#", "\\#" ],
  [ u"_", "\\_" ],
  [ u"≥", "$\\ge$" ],   # Math operators
  [ u"≤", "$\\le$" ],
  [ u"≠", "$\\neq$" ],
  [ u"©", "\copyright" ], # Misc
  [ u"ı", "{\\i}" ],
  [ u"µ", "$\\mu$" ],
  [ u"°", "$\\deg$" ],
  [ u"‘", "`" ],    #Quotes
  [ u"’", "'" ],
  [ u"“", "``" ],
  [ u"”", "''" ],
  [ u"‚", "," ],
  [ u"„", ",," ],
]




lista_1 = ['02', '93', '00', '98', '01', '97', '03', '04', '05', '07', '06', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18']
lista_2 = ['19', '20']
lista_3 = ['21']
lista_4 = ['22']



#-----------------------------------------------------------------

def normaliza(tabla,texto):
    normalizado = texto
    for [unicode,latex] in tabla:
        normalizado = normalizado.replace(latex,unicode)
    return normalizado


#-----------------------------------------------------------


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

#-----------------------------------------------------------------

def deserializar(linea):
    return json.loads(linea)

#-----------------------------------------------------------------

def insertar_carpeta(client, index_name, lista):
    for carpeta_pequeña in lista:
        # Construir la ruta completa a la carpeta
        carpeta_completa = os.path.join("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/unarXive_230324_open_subset", carpeta_pequeña)
        files = [f for f in os.listdir(carpeta_completa)]
        start_time = time.time()
        insertados = 0
        print(carpeta_completa)
        for f in files:
            print(f)
            nombre = os.path.join(carpeta_completa, f)
            print(str(nombre))
            insertados += insertar_json_serializado(client, index_name, nombre)
    print("--- %s seconds ---" % (time.time() - start_time))
    print("--- %d insertados ---" % (insertados))
    
#-----------------------------------------------------------------

def insertar_json_serializado(client, index_name, json_file):
    # Abre el archivo JSONL
    with open(json_file, "r") as f:
        datos = f.readlines()
        # Itera sobre cada línea del archivo JSONL
        i = 0
        for line in datos:
            # Carga el JSON de la línea actual
            line_json = json.loads(line)
            # Extrae los campos a indexar

            _id = line_json["paper_id"]
            disciplina = line_json["discipline"]
            titulo = line_json["metadata"]["title"]
            titulo = titulo.replace("\n", " " if titulo.endswith(" ") else "")
            titulo = re.sub(r' {2,}', ' ', titulo)
            titulo = normaliza(latexAccents, titulo)
            categoria = line_json["metadata"]["categories"]
            autores = line_json["metadata"]["authors"]
            autores = autores.replace("\n", " " if autores.endswith(" ") else "")
            autores = re.sub(r' {2,}', ' ', autores)
            autores = normaliza(latexAccents, autores)
            # Serializa el JSON completo
            documento_serializado = json.dumps(line_json)
            # Crea un nuevo documento con el JSON completo serializado
            documento = {
                "paper_id": _id,  # Se incluye el paper_id
                "discipline": disciplina,
                "title": titulo,
                "category": categoria,
                "authors": autores,
                "json_data": documento_serializado  # Se incluye el JSON completo serializado
            }
            # Inserta el documento en OpenSearch
            client.index(index=index_name, body=documento)
            i = i + 1
            print("i: " + str(i))
    print("Data inserted successfully.")
    return i

#-----------------------------------------------------------------


def obtener_numero_campos_ocupados(client, index_name):
    # Obtener el mapping del índice
    mapping = client.indices.get_mapping(index=index_name)

    # Contar el número de campos en el mapping
    numero_campos_ocupados = len(mapping[index_name]["mappings"]["properties"])

    return numero_campos_ocupados

#-----------------------------------------------------------------

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

#-----------------------------------------------------------------

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


#-----------------------------------------------------------------

def crear_indice(indice, client):
    index_name = indice
    index_body = {
        'settings': {
            'index': {
            'number_of_shards': 1
            }
        }
    }
    response = client.indices.create(index_name, body=index_body)
    print("Se ha creado el índice")
    return response

#-----------------------------------------------------------------

# # Set up the opensearch-py version of the document
# Movie.init(using=client)
# doc = Movie(meta={'id': 1}, title='Moneyball', director='Bennett Miller', year='2011')
# response = doc.save(using=client)



# s = Search(using=client, index="my-dsl-index2") \
#     .filter("term", year="2011") \
#     .query("match", title="Moneyball")

# response = s.execute()


# new_settings = {
#     "index.mapping.total_fields.limit": 20000  # Define el nuevo límite de campos totales
# }

# Actualiza la configuración del índice
#client.indices.put_settings(index=index_name, body=new_settings)

#print(f"Updated total fields limit for index '{index_name}'.")
#json_file = "../datos/un_json.jsonl"
#insertar_json(client, index_name, json_file)

#-----------------------------------------------------------------

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

#---------------------------------------------------------

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
            print("Contenido de 'json_data':", documento_encontrado["json_data"])
            return True
    return False

#---------------------------------------------------------

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


#----------------------------------------------------------

def verificar_insercion_titulo(client, index_name, titulo_buscado):
    # Realiza una búsqueda utilizando el título como filtro
    resultado = client.search(index=index_name, body={"query": {"match": {"title": titulo_buscado}}})

    # Verifica si se encontraron documentos
    hits = resultado["hits"]["hits"]
    if hits:
        # El primer hit contiene el documento encontrado
        documento_encontrado = hits[0]
        # Devuelve el _id del documento encontrado
        return documento_encontrado["paper_id"]
    return None



#----------------------------------------------------------------


def verificar_insercion_autor(client, index_name, autor_buscado):
    # Realiza una búsqueda utilizando el título como filtro
    resultado = client.search(index=index_name, body={"query": {"match": {"authors": autor_buscado}}})

    # Verifica si se encontraron documentos
    hits = resultado["hits"]["hits"]
    if hits:
        # El primer hit contiene el documento encontrado
        documento_encontrado = hits[0]["_source"]
        # Verifica si el campo 'json_data' está presente en el documento
        if "json_data" in documento_encontrado:
            print("Contenido de 'json_data':", documento_encontrado["json_data"])
            return True
    return False

#-------------------------------------------------------------

def buscar_papers_por_autor(client, index_name, autor):
    # Realiza una búsqueda utilizando el autor como filtro
    resultado = client.search(index=index_name, body={"query": {"match": {"authors": autor}}})

    # Lista para almacenar los IDs de los papers encontrados
    ids_papers = []

    # Verifica si se encontraron documentos
    hits = resultado["hits"]["hits"]
    if hits:
        # Itera sobre los hits y extrae el ID de cada documento
        for hit in hits:
            ids_papers.append(hit["_source"]["paper_id"])

    return ids_papers

#---------------------------------------------------------------


def buscar_papers_por_titulo(client, index_name, titulo_buscado):
    # Realiza una búsqueda utilizando el título como filtro
    resultado = client.search(index=index_name, body={"query": {"term": {"title.keyword": titulo_buscado}}})

    # Lista para almacenar los IDs de los papers encontrados
    ids_papers = []

    # Verifica si se encontraron documentos
    hits = resultado["hits"]["hits"]
    if hits:
        # Itera sobre los hits y extrae el ID de cada documento
        for hit in hits:
            ids_papers.append(hit["_source"]["paper_id"])

    return ids_papers




###################################################


# def main_indexar():
#     client = conexion()
#     index_name = "indice_1"
#     # response = crear_indice(index_name, client)
#     # print(str(response))
#     insertar_carpeta(client, index_name, lista_4)
#     #insertar_carpeta("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/unarXive_230324_open_subset/17/", client, index_name)
#     #imprimir_numdoc_indice(index_name, client)

def main_buscar():
    client = conexion()
    index_name = "indice_1"
    #verificar_insercion_titulo(client, index_name, "Law of Iterated Logarithms and Fractal Properties of the KPZ Equation")
    #verificar_insercion_autor(client, index_name, "Sayan Das")
    # autor_buscado = "Sayan Das"
    # papers_del_autor = buscar_papers_por_autor(client, index_name, autor_buscado)
    # print("Papers del autor '{}':".format(autor_buscado))
    # for paper_id in papers_del_autor:
    #     print(paper_id)
    titulo_buscado = "Dark matter searches and energy accumulation and release in materials"
    # Llamada a la función buscar_papers_por_titulo
    papers_encontrados = buscar_papers_por_titulo(client, index_name, titulo_buscado)
    # Imprimir los IDs de los papers encontrados
    if papers_encontrados:
        print("Papers encontrados con el título '{}':".format(titulo_buscado))
        for paper_id in papers_encontrados:
            print(paper_id)
    else:
        print("No se encontraron papers con el título '{}'.".format(titulo_buscado))

# def main_probar():
#     for carpeta_pequeña in lista_carpetas_48:
#         # Construir la ruta completa a la carpeta
#         carpeta_completa = os.path.join("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/unarXive_230324_open_subset", carpeta_pequeña)
#         files = [f for f in os.listdir(carpeta_completa)]
#         insertados = 0
#         print("Insertando documentos de la carpeta:", carpeta_pequeña)
#         for f in files:
#             nombre = os.path.join(carpeta_completa, f)
#             print(nombre)


############################################################

main_buscar()



