from opensearchpy import OpenSearch
from opensearch_dsl import Search, Document
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
from elasticsearch_client import ElasticsearchClient
# from model_processor import ModelProcessor

app = Flask(__name__)
CORS(app)

# Para configurar las sesiones de usuario en Flask
app.config['SECRET_KEY'] = os.urandom(24) # para establecer la clave para la sesion de usuario en flask
app.config['SESSION_TYPE'] = 'filesystem'  # Puedes elegir otros métodos de almacenamiento
Session(app)

########################################################################################

# El nombre del índice de la BD
index_name = "indice_1"

#################### Funciones para modificar las variables de sesion ##################

@app.before_request
def init_session():
    if 'paper_id' not in session:
        session['paper_id'] = ""
    if 'bibliografia' not in session:
        session['bibliografia'] = ""
    if 'parrafo_cita' not in session:
        session['parrafo_cita'] = ""
    
#---------------------------------------------------------------------------------------

def modify_paper_id(new_paper_id):
    print("Modificando el paper_id de: " + str(session['paper_id']) + " a " + str(new_paper_id))
    session['paper_id'] = new_paper_id
    print("Nuevo paper_id: " + str(session['paper_id']))

def modify_bibliografia(new_bibliografia):
    session['bibliografia'] = new_bibliografia

def modify_parrafo_cita(new_parrafo_cita):
    session['parrafo_cita'] = new_parrafo_cita


################################## ElasticSearch ######################################

client = ElasticsearchClient()


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
        modify_paper_id(PDFProcessor.extraer_arxiv(pdf_text))
        print("Id del documento subido:", session['paper_id'])
        #####client = conexion()
        #verificar_conexion(client)
        # titulo = obtener_titulo_por_paper_id(client, index_name, session['paper_id'])
        client = ElasticsearchClient()
        titulo = client.obtener_titulo_por_paper_id(index_name, session['paper_id'])
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
            #client = conexion()
            #verificar_conexion(client)
            # titulo = obtener_titulo_por_paper_id(client, index_name, session['paper_id']) #buscarlo en opensearch por id del paper
            client = ElasticsearchClient()
            titulo = client.obtener_titulo_por_paper_id(index_name, session['paper_id'])
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
        # client = conexion()
        # # Obtener la bibliografía
        # resultado = obtener_bibliografia_texto_parrafo_seleccion(client, index_name, session['paper_id'], selected_text)
        client = ElasticsearchClient()
        resultado = client.obtener_bibliografia_texto_parrafo_seleccion(index_name, session['paper_id'], selected_text)
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
    # print(session['bibliografia'])
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
    # client = conexion()
    # extraemos el paper_id del arxiv de la referencia
    paper_id_referencia = PDFProcessor.extraer_arxiv_de_entry_raw(citation)
    print("paper id de la referencia:", paper_id_referencia)
    # obtenemos el cuerpo del json correspondiente al paper_id de la referencia
    # texto_del_cuerpo_documento_referencia = obtener_json_por_paper_id_u_obtener_texto(client, index_name, paper_id_referencia)
    client = ElasticsearchClient()
    texto_del_cuerpo_documento_referencia = client.obtener_json_por_paper_id_u_obtener_texto(index_name, paper_id_referencia)
    #devolver el texto del json al frontend
    # en caso de que me devuelva que no está en la bd, buscar en archive el paper y devolverlo en forma de texto
    # return texto_del_cuerpo_documento_referencia
    #print('Cuerpo del json mandado al frontend:', texto_del_cuerpo_documento_referencia)
    return texto_del_cuerpo_documento_referencia

#------------------------------------------------------------------------------------

# para mandar al backend el texto del json que se ha referenciado para poder usar el modelo
@app.route('/sendReferencedJsonToBackend', methods=['POST'])
def receive_referenced_json():
    data = request.get_json()
    referencedjsontext = data.get('referencedjsontextandselectedtext')
    selectedText = data.get('selectedText')

    if referencedjsontext and selectedText:
        print('Texto JSON recibido desde el frontend:', referencedjsontext)
        print('Texto seleccionado recibido desde el frontend:', selectedText)
        # Aquí ahora habría que usar estos textos para comparar el JSON con la cita con el modelo y
        # devolver los resultados del modelo
        # modelP = ModelProcessor()
        # similitud = modelP.obtener_similitud_entre_cita_y_articulo(referencedjsontext, selectedText, model_processor.model, model_processor.vocabulary)
        print('Similitud entre la cita y el artículo:', similitud)
        return jsonify({'message': 'Textos recibidos con éxito'}), 200
    else:
        return jsonify({'error': 'No se proporcionaron todos los textos necesarios'}), 400

######################################################################################

if __name__ == "__main__":
    app.run(debug=True)
