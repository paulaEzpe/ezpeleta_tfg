# def conexion():
#     host = 'localhost'
#     port = 9200
#     auth = ('admin', 'admin') # For testing only. Don't store credentials in code.
#     ca_certs_path = '/full/path/to/root-ca.pem' # Provide a CA bundle if you use intermediate CAs with your root CA.

    
#     # Create the client with SSL/TLS enabled, but hostname verification disabled.
#     client = OpenSearch(
#         hosts = [{'host': host, 'port': port}],
#         http_compress = True, # enables gzip compression for request bodies
#         http_auth = auth,
#         use_ssl = True,
#         verify_certs = False,
#         ssl_assert_hostname = False,
#         ssl_show_warn = False,
#         ca_certs = ca_certs_path
#     )
#     return client


# def verificar_conexion(client):
#     try:
#         info_cluster = client.info()
#         if info_cluster:
#             print("¡Conexión establecida correctamente!")
#             print("Información del clúster:", info_cluster)
#             return True
#         else:
#             print("No se pudo obtener la información del clúster.")
#             return False
#     except Exception as e:
#         print("Error al intentar obtener información del clúster:", e)
#         return False

#------------------------------------------------------------------------------------

# def obtener_titulo_por_paper_id(client, index_name, paper_id):
#     # Realiza una búsqueda utilizando el paper_id como filtro
#     resultado = client.search(index=index_name, body={"query": {"term": {"paper_id": session['paper_id']}}}, _source=["title"])
#     hits = resultado["hits"]["hits"]
#     # Verifica si hay resultados
#     if hits:
#         for hit in hits:
#             return hit["_source"]["title"]  # Devuelve el título del documento encontrado
#     else:
#         return None  # Devuelve None si no se encontró ningún documento con el paper_id dado

#------------------------------------------------------------------------------------

# Función que devuelve el texto del cuerpo de un documento en formato JSON, dado su paper_id
# def obtener_json_por_paper_id_u_obtener_texto(client, index_name, paper_id_referencia):
#     resultado = client.search(
#         index=index_name,
#         body={
#             "query": {
#                 "match": {
#                     "paper_id": paper_id_referencia
#                 }
#             }
#         }
#     )
#     # hits = resultado["hits"]["hits"]
#     # Realiza una búsqueda utilizando el paper_id como filtro
#     # documento_especifico = resultado["hits"]["_source"]
#     print("El id del docukento que se esta buscando es:", paper_id_referencia)
#     hits = resultado["hits"]["hits"]
#     if hits: 
#         documento_especifico = hits[0]["_source"]
#         # Acceder al campo json_data para obtener el documento serializado
#         documento_serializado = documento_especifico["json_data"]

#         # Deserializar el documento serializado para obtener el documento original
#         documento_original = json.loads(documento_serializado)

#         # Acceder al campo body_text del documento original
#         body_text = documento_original["body_text"]

#         texto_cuerpo_json = ""

#         for obj in body_text:
#             # cojo el parrafo
#             texto = obj["text"]
#             texto_parrafo_limpio = TextProcessor.limpiar_texto(texto)
#             texto_parrafo = ' '.join(texto_parrafo_limpio)
#             texto_cuerpo_json += texto_parrafo + "\n"
#         return texto_cuerpo_json
#     else:
#         print("como no se ha encontrado el documento en la base de datos, lo descargo y extraigo el texto")
#         # return "No se ha podido obtener el json correspondiente ya que no se encuentra en la base de datos"
#         # NUEVO
#         # Si el paper_id no se encuentra en la base de datos, descargar y extraer el PDF
#         texto_pdf, _ = PDFProcessor.descargar_y_extraer_texto_pdf_arxiv(paper_id_referencia, "../datos/")
#         return texto_pdf
        

#------------------------------------------------------------------------------------

# def obtener_bibliografia_texto_parrafo_seleccion(client, index_name, paper_id, cita):
#     consulta = {"query": {"match": {"paper_id": session['paper_id']}}}   
#     # Realizar la consulta para obtener el documento específico
#     resultado = client.search(index=index_name, body=consulta)
#     # Obtener el documento específico de los resultados
#     documento_especifico = resultado["hits"]["hits"][0]["_source"]

#     # Acceder al campo json_data para obtener el documento serializado
#     documento_serializado = documento_especifico["json_data"]

#     # Deserializar el documento serializado para obtener el documento original
#     documento_original = json.loads(documento_serializado)

#     # Acceder al campo body_text del documento original
#     body_text = documento_original["body_text"]
#     # cojo las referencias de las citas del documento original
#     bibliografia = documento_original["bib_entries"]

#     #para almacenar el parrafo en el que se encuentra la cita
#     parrafo_cita = ""

#     contiene_cita = False
#     bibliografia_completa = ""  # Inicializar el string de la bibliografía

#     texto_cita_limpio = TextProcessor.limpiar_texto(cita)

#     for obj in body_text:
#         # cojo el parrafo
#         texto = obj["text"]
#         # cojo las citas del parrafo
#         citas = obj["cite_spans"]


#         # Tengo que moidificar esto para que en vez de coger texto tal cual de la cita, primero lo tokenice, y lo compare con los párrafos, necesitando un 90% de coincnidencia entre las palabras, por si la selección de la cita, se come algo del principio o del final de una palabra
#         texto_parrafo_limpio = TextProcessor.limpiar_texto(texto)
#         texto_parrafo = ' '.join(texto_parrafo_limpio)
        
#         if all(palabra in texto_parrafo_limpio for palabra in texto_cita_limpio):
#             contiene_cita = True
#             parrafo_cita = texto
#             break

#     if contiene_cita:
#         #print(texto)
#         bibliografia_completa = ""  # Inicializar el string de la bibliografía
#         # si contiene la cita, extraigo las citas del parrafo correspondiente al texto que ha seleccionado el usuario
#         citas_seleccionadas = TextProcessor.extraer_citas(texto)
#         # ahora en citas_seleccionadas, estan las citas que ha seleccionado el usuario al seleccionar texto en el párrafo
#         #ahora las contrasto con las citas que aparecen en el parrfo correspondiente a la seleccion
#         for cita in citas_seleccionadas:
#             # Obtener el identificador de la cita
#             identificador = cita.split(":")[1].split("}")[0]
#             if any(identificador == span["ref_id"] for span in obj["cite_spans"]):
#                 # Construir el string de la bibliografía
#                 bibliografia_completa += f"Cita {{cite:{identificador}}}\n"
#                 # en caso de que exista, hay que ir a buscarla a las referencias
#                 bibliografia_raw = bibliografia[identificador]["bib_entry_raw"]
#                 bibliografia_completa += f"Bibliografía: {bibliografia_raw}\n\n"
#             else:
#                 bibliografia_completa += f"La cita {{cite:{cita}}} no coincide con ninguna cita en obj.\n"
#     else:
#         bibliografia_completa = "El string no está presente en ningún objeto body_text."

#     return {"bibliografia": bibliografia_completa, "parrafo_cita": parrafo_cita}
