"""-------------------------------------------------------------------------
Nombre del archivo: high_client.py
Autora:             Paula Ezpeleta Castrillo
Fecha de creación:  24/03/2024
Descripción:        Archivo que contiene el código necesario para todas las operaciones con OpenSearch
-------------------------------------------------------------------------"""

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

#---------------------------------------------------------

def obtener_body_documento_y_comparar_string_presente(client, index_name, paper_id, cita):
    consulta = {"query": {"match": {"paper_id": paper_id}}}   
    # Realizar la consulta para obtener el documento específico
    resultado = client.search(index=index_name, body=consulta)
    # Obtener el documento específico de los resultados
    documento_especifico = resultado["hits"]["hits"][0]["_source"]

    # Acceder al campo json_data para obtener el documento serializado
    documento_serializado = documento_especifico["json_data"]

    # Deserializar el documento serializado para obtener el documento original
    documento_original = json.loads(documento_serializado)

    # Acceder al campo body_text del documento original
    body_text = documento_original["body_text"]
    # cojo las referencias de las citas del documento original
    bibliografia = documento_original["bib_entries"]

    contiene_cita = False

    texto_cita_limpio = limpiar_texto(cita)

    for obj in body_text:
        # cojo el parrafo
        texto = obj["text"]
        # cojo las citas del parrafo
        citas = obj["cite_spans"]

        texto_parrafo_limpio = limpiar_texto(texto)
        texto_parrafo = ' '.join(texto_parrafo_limpio)
        
        if all(palabra in texto_parrafo_limpio for palabra in texto_cita_limpio):
            contiene_cita = True
            break

    if contiene_cita:
        print("El string está presente en al menos uno de los objetos body_text.")
        # si contiene la cita, extraigo las citas del parrafo correspondiente al texto que ha seleccionado el usuario
        citas_seleccionadas = extraer_citas(texto)
        # ahora en citas_seleccionadas, estan las citas que ha seleccionado el usuario al seleccionar texto en el párrafo
        #ahora las contrasto con las citas que aparecen en el parrfo correspondiente a la seleccion
        for cita in citas_seleccionadas:
            # Obtener el identificador de la cita
            identificador = cita.split(":")[1].split("}")[0]
            if any(identificador == span["ref_id"] for span in obj["cite_spans"]):
                print(f"Cita {{cite:{identificador}}}")
                # en caso de que exista, hay que ir a buscarla a las referencias
                bibliografia_raw = bibliografia[identificador]["bib_entry_raw"]
                print("Bibliografía:", bibliografia_raw)
            else:
                print(f"La cita {{cite:{cita}}} no coincide con ninguna cita en obj.")
    else:
        print("El string no está presente en ningún objeto body_text.")
        
        

#-----------------------------------------------------

def buscar_referencias_arxiv(client, index_name, paper_id):
    print("Buscando referencias de arXiv en el documento con paper_id:", paper_id)
    consulta = {"query": {"match": {"paper_id": paper_id}}}   
    # Realizar la consulta para obtener el documento específico
    resultado = client.search(index=index_name, body=consulta)
    # Obtener el documento específico de los resultados
    documento_especifico = resultado["hits"]["hits"][0]["_source"]

    # Acceder al campo json_data para obtener el documento serializado
    documento_serializado = documento_especifico["json_data"]

    # Deserializar el documento serializado para obtener el documento original
    documento_original = json.loads(documento_serializado)

    # Acceder a las referencias del documento original
    bibliografia = documento_original["bib_entries"]

    referencias_arxiv = []
    
    for key, entry in bibliografia.items():
        bib_entry_raw = entry["bib_entry_raw"]
        if "arxiv" in bib_entry_raw.lower():
            referencias_arxiv.append(bib_entry_raw)
            print(f"Referencia arXiv encontrada: {bib_entry_raw}")
    
    if not referencias_arxiv:
        print("No se encontraron referencias de arXiv.")
    return paper_id, referencias_arxiv



def verificar_referencias_arxiv_en_base_de_datos(client, index_name, referencias_arxiv, file_name, documento):
    referencias_encontradas = []
    with open(file_name, 'a') as file:
        for referencia in referencias_arxiv:
            # Extraer el identificador de arXiv de la referencia
            arxiv_id = extraer_arxiv_id(referencia)
            if arxiv_id:
                consulta = {"query": {"match": {"paper_id": arxiv_id}}}
                resultado = client.search(index=index_name, body=consulta)
                if resultado["hits"]["total"]["value"] > 0:
                    referencias_encontradas.append(arxiv_id)
                    print(f"Referencia arXiv {arxiv_id} encontrada en la base de datos.")
                    # Escribir el paper_id y el arxiv_id en el archivo
                    file.write(f"Paper ID: {documento}, Referencia arXiv: {arxiv_id}\n")
                else:
                    print(f"Referencia arXiv {arxiv_id} no encontrada en la base de datos.")
    return referencias_encontradas



def extraer_arxiv_id(referencia):
    # Extrae el identificador de arXiv de la referencia usando una expresión regular
    import re
    pattern = r'arxiv:\s*(\d+\.\d+|[a-z\-]+/\d+v\d+)'  # Patrón para arXiv ID
    match = re.search(pattern, referencia.lower())
    if match:
        return match.group(1)
    return None


def obtener_primeros_paper_ids(client, index_name, num_documentos):
    consulta = {
        "query": {
            "match_all": {}
        },
        "size": num_documentos,
        "_source": ["paper_id"]  # Solo devolver el campo paper_id
    }
    
    resultados = client.search(index=index_name, body=consulta)
    documentos = resultados["hits"]["hits"]
    
    paper_ids = [doc["_source"]["paper_id"] for doc in documentos]
    
    return paper_ids

def obtener_ultimos_paper_ids(client, index_name, num_documentos):
    consulta = {
        "query": {
            "match_all": {}
        },
        "size": num_documentos,
        "sort": [
            {"_id": {"order": "desc"}}  # Ordenar por el campo _id en orden descendente
        ],
        "_source": ["paper_id"]  # Solo devolver el campo paper_id
    }
    
    resultados = client.search(index=index_name, body=consulta)
    documentos = resultados["hits"]["hits"]
    
    paper_ids = [doc["_source"]["paper_id"] for doc in documentos]
    
    return paper_ids




def main_arxiv():
    client = conexion()
    primeros_paper_ids = obtener_ultimos_paper_ids(client, "indice_1", num_documentos=2000)
    print(primeros_paper_ids)
    for documento in primeros_paper_ids:
        paper, referencias_arxiv = buscar_referencias_arxiv(client, "indice_1", documento)
        referencias_encontradas = verificar_referencias_arxiv_en_base_de_datos(client, "indice_1", referencias_arxiv, "referencias_encontradas.txt", paper)

###################################################


# def main_indexar():
#     client = conexion()
#     index_name = "indice_1"
#     # response = crear_indice(index_name, client)
#     # print(str(response))
#     insertar_carpeta(client, index_name, lista_4)
#     #insertar_carpeta("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/unarXive_230324_open_subset/17/", client, index_name)
#     #imprimir_numdoc_indice(index_name, client)

# def main_buscar():
#     client = conexion()
#     index_name = "indice_1"
#     obtener_body_documento_y_comparar_string_presente(client, index_name, "2201.01489", "The quark model calculations in the S01 partial wave, nonrelativistic or relativistic")
    #verificar_insercion_titulo(client, index_name, "Law of Iterated Logarithms and Fractal Properties of the KPZ Equation")
    #verificar_insercion_autor(client, index_name, "Sayan Das")
    # autor_buscado = "Sayan Das"
    # papers_del_autor = buscar_papers_por_autor(client, index_name, autor_buscado)
    # print("Papers del autor '{}':".format(autor_buscado))
    # for paper_id in papers_del_autor:
    #     print(paper_id)
    # titulo_buscado = "Dark matter searches and energy accumulation and release in materials"
    # # Llamada a la función buscar_papers_por_titulo
    # papers_encontrados = buscar_papers_por_titulo(client, index_name, titulo_buscado)
    # # Imprimir los IDs de los papers encontrados
    # if papers_encontrados:
    #     print("Papers encontrados con el título '{}':".format(titulo_buscado))
    #     for paper_id in papers_encontrados:
    #         print(paper_id)
    # else:
    #     print("No se encontraron papers con el título '{}'.".format(titulo_buscado))

#---------------------------------------------------------------

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

main_arxiv()



