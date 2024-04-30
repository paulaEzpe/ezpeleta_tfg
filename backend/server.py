from opensearchpy import OpenSearch
from opensearch_dsl import Search
from opensearch_dsl import Document, Text, Keyword
from flask import Flask, request, send_file, jsonify, url_for, Response, redirect, send_from_directory, session
from flask_session import Session
from flask_cors import CORS
import re
import os
import json
import requests
from io import BytesIO 
import PyPDF2

# Importar las clases de los otros módulos
from pdf_processor import PDFProcessor
from text_processor import TextProcessor

app = Flask(__name__)
CORS(app)

# Para configurar las sesiones de usuario en Flask
app.config['SECRET_KEY'] = os.urandom(24) # para establecer la clave para la sesion de usuario en flask
app.config['SESSION_TYPE'] = 'filesystem'  # Puedes elegir otros métodos de almacenamiento
Session(app)

####################################################################

# El nombre del índice de la BD
index_name = "indice_1"

####################Funciones para modificar las variables de sesion######################

@app.before_request
def init_session():
    if 'paper_id' not in session:
        session['paper_id'] = ""
    if 'bibliografia' not in session:
        session['bibliografia'] = ""
    if 'parrafo_cita' not in session:
        session['parrafo_cita'] = ""
    
#-------------------------------------------------------------------------------------

def modify_paper_id(new_paper_id):
    session['paper_id'] = new_paper_id

def modify_bibliografia(new_bibliografia):
    session['bibliografia'] = new_bibliografia

def modify_parrafo_cita(new_parrafo_cita):
    session['parrafo_cita'] = new_parrafo_cita


################################## Gestiones con ElasticSearch ######################

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


def verificar_conexion(client):
    try:
        info_cluster = client.info()
        if info_cluster:
            print("¡Conexión establecida correctamente!")
            print("Información del clúster:", info_cluster)
            return True
        else:
            print("No se pudo obtener la información del clúster.")
            return False
    except Exception as e:
        print("Error al intentar obtener información del clúster:", e)
        return False

#------------------------------------------------------------------------------------

def obtener_titulo_por_paper_id(client, index_name, paper_id):
    # Realiza una búsqueda utilizando el paper_id como filtro
    resultado = client.search(index=index_name, body={"query": {"term": {"paper_id": session['paper_id']}}}, _source=["title"])
    hits = resultado["hits"]["hits"]
    # Verifica si hay resultados
    if hits:
        for hit in hits:
            return hit["_source"]["title"]  # Devuelve el título del documento encontrado
    else:
        return None  # Devuelve None si no se encontró ningún documento con el paper_id dado

#------------------------------------------------------------------------------------

# Función que devuelve el texto del cuerpo de un documento en formato JSON, dado su paper_id
def obtener_json_por_paper_id_u_obtener_texto(client, index_name, paper_id_referencia):
    resultado = client.search(
        index=index_name,
        body={
            "query": {
                "match": {
                    "paper_id": paper_id_referencia
                }
            }
        }
    )
    # hits = resultado["hits"]["hits"]
    # Realiza una búsqueda utilizando el paper_id como filtro
    # documento_especifico = resultado["hits"]["_source"]
    print("El id del docukento que se esta buscando es:", paper_id_referencia)
    hits = resultado["hits"]["hits"]
    if hits: 
        documento_especifico = hits[0]["_source"]
        # Acceder al campo json_data para obtener el documento serializado
        documento_serializado = documento_especifico["json_data"]

        # Deserializar el documento serializado para obtener el documento original
        documento_original = json.loads(documento_serializado)

        # Acceder al campo body_text del documento original
        body_text = documento_original["body_text"]

        texto_cuerpo_json = ""

        for obj in body_text:
            # cojo el parrafo
            texto = obj["text"]
            texto_parrafo_limpio = TextProcessor.limpiar_texto(texto)
            texto_parrafo = ' '.join(texto_parrafo_limpio)
            texto_cuerpo_json += texto_parrafo + "\n"
        return texto_cuerpo_json
    else:
        print("como no se ha encontrado el documento en la base de datos, lo descargo y extraigo el texto")
        # return "No se ha podido obtener el json correspondiente ya que no se encuentra en la base de datos"
        # NUEVO
        # Si el paper_id no se encuentra en la base de datos, descargar y extraer el PDF
        texto_pdf, _ = PDFProcessor.descargar_y_extraer_texto_pdf_arxiv(paper_id_referencia, "../datos/")
        return texto_pdf
        

#------------------------------------------------------------------------------------

def obtener_bibliografia_texto_parrafo_seleccion(client, index_name, paper_id, cita):
    consulta = {"query": {"match": {"paper_id": session['paper_id']}}}   
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

    #para almacenar el parrafo en el que se encuentra la cita
    parrafo_cita = ""

    contiene_cita = False
    bibliografia_completa = ""  # Inicializar el string de la bibliografía

    texto_cita_limpio = TextProcessor.limpiar_texto(cita)

    for obj in body_text:
        # cojo el parrafo
        texto = obj["text"]
        # cojo las citas del parrafo
        citas = obj["cite_spans"]


        # Tengo que moidificar esto para que en vez de coger texto tal cual de la cita, primero lo tokenice, y lo compare con los párrafos, necesitando un 90% de coincnidencia entre las palabras, por si la selección de la cita, se come algo del principio o del final de una palabra
        texto_parrafo_limpio = TextProcessor.limpiar_texto(texto)
        texto_parrafo = ' '.join(texto_parrafo_limpio)
        
        if all(palabra in texto_parrafo_limpio for palabra in texto_cita_limpio):
            contiene_cita = True
            parrafo_cita = texto
            break

    if contiene_cita:
        #print(texto)
        bibliografia_completa = ""  # Inicializar el string de la bibliografía
        # si contiene la cita, extraigo las citas del parrafo correspondiente al texto que ha seleccionado el usuario
        citas_seleccionadas = TextProcessor.extraer_citas(texto)
        # ahora en citas_seleccionadas, estan las citas que ha seleccionado el usuario al seleccionar texto en el párrafo
        #ahora las contrasto con las citas que aparecen en el parrfo correspondiente a la seleccion
        for cita in citas_seleccionadas:
            # Obtener el identificador de la cita
            identificador = cita.split(":")[1].split("}")[0]
            if any(identificador == span["ref_id"] for span in obj["cite_spans"]):
                # Construir el string de la bibliografía
                bibliografia_completa += f"Cita {{cite:{identificador}}}\n"
                # en caso de que exista, hay que ir a buscarla a las referencias
                bibliografia_raw = bibliografia[identificador]["bib_entry_raw"]
                bibliografia_completa += f"Bibliografía: {bibliografia_raw}\n\n"
            else:
                bibliografia_completa += f"La cita {{cite:{cita}}} no coincide con ninguna cita en obj.\n"
    else:
        bibliografia_completa = "El string no está presente en ningún objeto body_text."

    return {"bibliografia": bibliografia_completa, "parrafo_cita": parrafo_cita}


################################### Rutas #############################################

@app.route('/datos/<path:path>')
def serve_pdf(path):
    return send_from_directory('/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/web2/datos', path)

# Para recibir el pdf 
@app.route("/uploadPDFText", methods=["POST"])
def upload_pdf_text():
    data = request.json
    pdf_text = data.get('pdfText')
    if pdf_text is None:
        return {"error": "No se proporcionó el texto del PDF"}, 400
    else:
        # Buscar el documento en elasticsearch
        #paper_id = extraer_arxiv(pdf_text)
        # pdf_processor = PDFProcessor()
        modify_paper_id(PDFProcessor.extraer_arxiv(pdf_text))
        print("Id del documento subido:", session['paper_id'])
        client = conexion()
        #verificar_conexion(client)
        titulo = obtener_titulo_por_paper_id(client, index_name, session['paper_id'])
        if titulo is not None:
            print("Título del documento encontrado:", titulo)
        else:
            print("No se encontró ningún documento con el paper_id dado.")
        
        # Guardar el pdf en un .txt
        with open('pdf_text.txt', 'w') as file:
            file.write(pdf_text)
        return {"message": "Texto del PDF recibido y guardado exitosamente en pdf_text.txt."}

#-------------------------------------------------------------------------------------

# Para descargar el pdf del id que mete el usuario
@app.route("/uploadInputPdfId", methods=["POST"])
def upload_input_text():
    data = request.json
    input_text = data.get('inputText')
    if input_text is None:
        return {"error": "No se proporcionó el texto del input"}, 400
    else:
        # Descargar el PDF y obtener su ruta en el servidor
        #paper_id=input_text
        modify_paper_id(input_text)
        print("Id del documento buscado y descargado:", session['paper_id'])
        pdf_path = PDFProcessor.descargar_pdf_arxiv(session['paper_id'], "../datos/")
        print("lo he descargadoi sin problemas")
        if pdf_path:
            # Devolver la ruta del PDF al cliente
            print(pdf_path)
            client = conexion()
            #verificar_conexion(client)
            titulo = obtener_titulo_por_paper_id(client, index_name, session['paper_id']) #buscarlo en opensearch por id del paper
            if titulo is not None:
                print("Título del documento encontrado:", titulo)
            else:
                print("No se encontró ningún documento con el paper_id dado.")
            return {"pdfUrl": pdf_path}
        else:
            return {"error": "No se pudo descargar el PDF remoto"}, 500


#-------------------------------------------------------------------------------------

# Para el texto seleccionado en el pdf por el usuario
@app.route("/uploadSelectedText", methods=["POST"])
def save_selected_text():
    data = request.json
    selected_text = data.get('selectedText')
    if selected_text is None:
        return {"error": "No se proporcionó texto seleccionado"}, 400
    else:
        # Mostrar el texto seleccionado en la terminal
        print("Paper_id ultimo obtenido: ", session['paper_id'])
        print('Texto seleccionado:', selected_text)
        # Filtrar el texto para que cuando corte una palabra con un guión seguido de \n reconstruya la palabra
        selected_text = selected_text.replace('-\n', '')
        # Filtrar el texto seleccionado para ponerlo todo en una linea 
        selected_text = selected_text.replace('\n', ' ')
        print('Texto seleccionado tras sustiruir saltos de linea y guiones:', selected_text)
        client = conexion()
        # Obtener la bibliografía
        resultado = obtener_bibliografia_texto_parrafo_seleccion(client, index_name, session['paper_id'], selected_text)
        # Acceder a la bibliografía
        bibliografia_obtenida = resultado["bibliografia"]
        # Acceder al párrafo correspondiente a la selección
        parrafo_obtenido = resultado["parrafo_cita"]
        parrafo_obtenido_str = json.dumps(parrafo_obtenido, indent=4)  # Convierte el JSON a una cadena con formato legible
        print(parrafo_obtenido_str)
        # Modificar la variable global de bibliografía
        modify_bibliografia(bibliografia_obtenida)
        # Modificar la variable global de parrafo_cita
        modify_parrafo_cita(parrafo_obtenido_str)
        # Devolver una respuesta indicando que la acción se ha completado correctamente
        return {"message": "Bibliografia guardada correctamente"}, 200

#------------------------------------------------------------------------------------

# para enviar al frontend la bibliografia obtenida con la funcion obtener_bibliografia_texto_parrafo_seleccion
@app.route('/getBibliography', methods=['GET'])
def get_received_text():
    # Aquí recupera el texto procesado anteriormente, por ejemplo, de la base de datos
    # Luego envía el texto al frontend
    print(session['bibliografia'])
    return session['bibliografia']

#------------------------------------------------------------------------------------

@app.route('/getTextParagraphSelection', methods=['GET'])
def get_received_paragraph_text():
    # Aquí recupera el texto procesado anteriormente, por ejemplo, de la base de datos
    # Luego envía el texto al frontend
    return session['parrafo_cita']

#------------------------------------------------------------------------------------

@app.route('/sendCitationToBackend', methods=['POST', 'GET'])
def receive_citation_from_frontend():
    # Obtener la cita del cuerpo de la solicitud JSON
    citation = request.json.get('citation')

    # Aquí puedes hacer lo que necesites con la cita recibida
    print('Cita recibida en el backend:', citation)
    # extraer el paper_id del entry_raw 
    client = conexion()
    # extraemos el paper_id del arxiv de la referencia
    paper_id_referencia = PDFProcessor.extraer_arxiv_de_entry_raw(citation)
    print("paper id de la referencia:", paper_id_referencia)
    # obtenemos el cuerpo del json correspondiente al paper_id de la referencia
    texto_del_cuerpo_documento_referencia = obtener_json_por_paper_id_u_obtener_texto(client, index_name, paper_id_referencia)
    #devolver el texto del json al frontend
    # en caso de que me devuelva que no está en la bd, buscar en archive el paper y devolverlo en forma de texto
    # return texto_del_cuerpo_documento_referencia
    #print('Cuerpo del json mandado al frontend:', texto_del_cuerpo_documento_referencia)
    return texto_del_cuerpo_documento_referencia


######################################################################################

if __name__ == "__main__":
    app.run(debug=True)
