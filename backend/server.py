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
import numpy as np

# Importar las clases de los otros módulos
from pdf_processor import PDFProcessor
from text_processor import TextProcessor
from elasticsearch_client import ElasticsearchClient
from model_processor import ModelProcessor

app = Flask(__name__)
CORS(app)

# Para configurar las sesiones de usuario en Flask
app.config['SECRET_KEY'] = os.urandom(24) # para establecer la clave para la sesion de usuario en flask
app.config['SESSION_TYPE'] = 'filesystem'  # Puedes elegir otros métodos de almacenamiento
Session(app)

########################################################################################

# El nombre del índice de la BD
index_name = "indice_1"
# Variable para que cargue los modelos en memoria únicamente una vez
modelP = ModelProcessor()

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
    return send_from_directory('../datos/', path)

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
        print('Texto del PDF:', pdf_text)
        pdf_path = PDFProcessor.descargar_pdf_arxiv(session['paper_id'], "../datos/")
        print("lo he descargadoi sin problemas")
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
        return {"pdfUrl": pdf_path,"tituloEncontrado": titulo is not None}


#-------------------------------------------------------------------------------------

# Para descargar el pdf del id que mete el usuario
@app.route("/uploadInputPdfId", methods=["POST"])
def upload_input_text():
    data = request.json
    input_text = data.get('inputText')
    if input_text is None:
        return {"error": "No se proporcionó el texto del input"}, 400
    else:
        # Suponiendo que `modify_paper_id` es una función que modifica el estado de `session['paper_id']`
        modify_paper_id(input_text)
        print("Id del documento buscado y descargado:", session['paper_id'])
        pdf_path = PDFProcessor.descargar_pdf_arxiv(session['paper_id'], "../datos/")
        print("lo he descargadoi sin problemas")
        titulo = None
        if pdf_path:
            print(pdf_path)
            client = ElasticsearchClient()
            titulo = client.obtener_titulo_por_paper_id(index_name, session['paper_id'])
            if titulo is not None:
                print("Título del documento encontrado:", titulo)
        else:
            print("No se pudo descargar el PDF remoto.")
            return {"error": "No se pudo descargar el PDF remoto"}, 500

        # Devolver pdf_path y la bandera de título encontrado
        return {"pdfUrl": pdf_path, "tituloEncontrado": titulo is not None}


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
        # AQUI HAY QUE GUARDAR EL TEXTO SELECCIONADO EN VARIABLE DE SESION#



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

@app.route('/sendCitationToBackend', methods=['POST'])
def receive_citation_from_frontend():
    # Obtener la cita del cuerpo de la solicitud JSON
    citation = request.json.get('citation')

    # Aquí puedes hacer lo que necesites con la cita recibida
    print('Cita recibida en el backend:', citation)

    # Extraer el paper_id del entry_raw 
    paper_id_referencia = PDFProcessor.extraer_arxiv_de_entry_raw(citation)
    print("paper id de la referencia:", paper_id_referencia)

    # Obtener el cuerpo del json correspondiente al paper_id de la referencia
    client = ElasticsearchClient()
    texto_del_cuerpo_documento_referencia, abstract_documento_referencia = client.obtener_json_por_paper_id_u_obtener_texto(index_name, paper_id_referencia)

    # Escribir en un fichero para debug (opcional)
    with open("fichero_obtendo_json_frontend_1.txt", 'w') as file:
        file.write(texto_del_cuerpo_documento_referencia)

    # Devolver el texto del json al frontend
    response_data = {
        "texto_del_cuerpo": texto_del_cuerpo_documento_referencia,
        "abstract": abstract_documento_referencia
    }

    return jsonify(response_data)


#------------------------------------------------------------------------------------

# para mandar al backend el texto del json que se ha referenciado para poder usar el modelo
@app.route('/sendReferencedJsonBodyToBackend', methods=['POST'])
def receive_referenced_json():
    data = request.get_json()
    referencedjsontext = data.get('referencedjsonbodytextandselectedtext')
    selectedText = data.get('selectedText')

    if referencedjsontext and selectedText:
        print('Texto JSON recibido desde el frontend:', referencedjsontext)
        print('Texto seleccionado recibido desde el frontend:', selectedText)

        # Dividir el texto completo en párrafos
        paragraphs = referencedjsontext.split('\n\n')
        #NUEVO: aqui si el referenced no esta en la bd, no estara separado en parrafos

        # Inicializar variables para almacenar el párrafo con las similitudes más altas
        max_similarity_paragraph = ""
        max_avg_similarity = 0
        similitudes = []
        similitudes_calculadas = []

        for paragraph in paragraphs:
            paragraph_str = str(paragraph)
            textP = TextProcessor()
            text_words, cite_words = textP.obtain_list_english_words(paragraph_str, selectedText)
            similitudes_parrafo = modelP.obtener_similitud_entre_cita_y_articulo(cite_words, text_words)
            print("Similitudes_parrafo:", similitudes_parrafo)
            
            if similitudes_parrafo:
                elementos = []

                for value in similitudes_parrafo:
                    if isinstance(value, np.ndarray):
                        # Si el elemento es un array, calcular el promedio de sus elementos
                        elementos.append(0)
                    else:
                        # Si el elemento no es un array, agregarlo directamente al total
                        elementos.append(value)

                print("elementos:", elementos)
                avg_similarity = np.mean(elementos)

            if avg_similarity > max_avg_similarity:
                max_avg_similarity = avg_similarity
                max_similarity_paragraph = paragraph_str
                similitudes = elementos

        # Devolver las similitudes y el párrafo con las similitudes más altas
        if max_similarity_paragraph:
            print("Similitudes:", similitudes)
            print("el tipo de datos de similitudes es:", type(similitudes))
            print("max similarity paragraph:", max_similarity_paragraph)
            similitudes = [value.tolist() if isinstance(value, np.ndarray) else float(value) for value in similitudes]
            return jsonify({'message': 'Similitudes calculadas con éxito', 'similitudes': similitudes, 'paragraph': max_similarity_paragraph}), 200
            
        else:
            print('No se pudo calcular la similitud entre la cita y el artículo.')
            return jsonify({'error': 'No se pudo calcular la similitud entre la cita y el artículo.'}), 500


# @app.route('/sendReferencedJsonBodyToBackend', methods=['POST'])
# def receive_referenced_json():
#     data = request.get_json()
#     referencedjsontext = data.get('referencedjsonbodytextandselectedtext')
#     #aqui habria que cogerlo de la variable de sesion en vez de aqui
#     selectedText = data.get('selectedText')

#     if referencedjsontext and selectedText:
#         print('Texto JSON recibido desde el frontend:', referencedjsontext)
#         print('Texto seleccionado recibido desde el frontend:', selectedText)
#         # Aquí ahora habría que usar estos textos para comparar el JSON con la cita con los modelos y
#         # devolver los resultados del modelo
#         print("Tipo de referencedjsontext:", type(referencedjsontext))
#         print("Tipo de selectedText:", type(selectedText))
#         referencedjsontext_str = str(referencedjsontext)
#         selectedText_str = str(selectedText)
#         textP = TextProcessor()
#         text_words, cite_words = textP.obtain_list_english_words(referencedjsontext_str, selectedText_str)
#         print("Las palabras de la cita son las siguientes: ", cite_words)
#         # Obtener similitudes usando todos los modelos
#         similitudes = modelP.obtener_similitud_entre_cita_y_articulo(cite_words, text_words)
#         # Imprimir las similitudes por terminal
#         for i, similitud in enumerate(similitudes):
#             print(f'Similitud entre la cita y el artículo (modelo {i+1}): {similitud}')
#         # Si alguna similitud está definida, devolver el resultado exitosamente
#         similitudes = [float(similitud) for similitud in similitudes]
#         if any(similitudes):
#             return jsonify({'message': 'Textos recibidos con éxito', 'similitudes': similitudes}), 200
#         else:
#             print('No se pudo calcular la similitud entre la cita y el artículo.')
#             return jsonify({'error': 'No se pudo calcular la similitud entre la cita y el artículo.'}), 500



@app.route('/sendReferencedJsonAbstractToBackend', methods=['POST'])
def receive_referenced_json_abstract():
    data = request.get_json()
    referencedjsonabstracttext = data.get('referencedjsonabstracttextandselectedtext')
    selectedText = data.get('selectedText')

    if referencedjsonabstracttext and selectedText:
        print('Texto JSON recibido desde el frontend:', referencedjsonabstracttext)
        print('Texto seleccionado recibido desde el frontend:', selectedText)
        # Aquí ahora habría que usar estos textos para comparar el JSON con la cita con los modelos y
        # devolver los resultados del modelo
        print("Tipo de referencedjsonabstracttext:", type(referencedjsonabstracttext))
        print("Tipo de selectedText:", type(selectedText))
        referencedjsonabstracttext_str = str(referencedjsonabstracttext)
        selectedText_str = str(selectedText)
        textP = TextProcessor()
        text_words, cite_words = textP.obtain_list_english_words(referencedjsonabstracttext_str, selectedText_str)
        print("Las palabras de la cita son las siguientes: ", cite_words)
        # Obtener similitudes usando todos los modelos
        similitudes = modelP.obtener_similitud_entre_cita_y_articulo(cite_words, text_words)
        # Imprimir las similitudes por terminal
        for i, similitud in enumerate(similitudes):
            print(f'Similitud entre la cita y el artículo (modelo {i+1}): {similitud}')
        # Si alguna similitud está definida, devolver el resultado exitosamente
        similitudes = [float(similitud) for similitud in similitudes]
        if any(similitudes):
            return jsonify({'message': 'Textos recibidos con éxito', 'similitudes': similitudes}), 200
        else:
            print('No se pudo calcular la similitud entre la cita y el artículo.')
            return jsonify({'error': 'No se pudo calcular la similitud entre la cita y el artículo.'}), 500

#------------------------------------------------------------------------------------

@app.route('/sendCitationForPolarityToBackend', methods=['POST'])
def receive_citation_polarity():
    data = request.get_json()
    selectedText = data.get('selectedText')

    if selectedText:
        print('Texto seleccionado recibido desde el frontend:', selectedText)
        print("Tipo de selectedText:", type(selectedText))
        selectedText_str = str(selectedText)
        textP = TextProcessor()
        cite_words = textP.obtain_list_english_words_from_body(selectedText_str)
        print("Las palabras de la cita son las siguientes: ", cite_words)
        # Obtener similitudes usando todos los modelos
        polaridades = modelP.calcular_polaridad(cite_words)
        polaridades_list = polaridades.tolist() if isinstance(polaridades, np.ndarray) else list(polaridades)
        print("Polaridades calculadas:", polaridades_list)

        return jsonify({'polaridades_list': polaridades_list})  # Ajustar el nombre de la clave aquí
    else:
        return jsonify({'error': 'No se recibió ningún texto seleccionado'}), 400
    
######################################################################################

if __name__ == "__main__":
    app.run(debug=True)
