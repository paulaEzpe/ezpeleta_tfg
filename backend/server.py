from opensearchpy import OpenSearch
from opensearch_dsl import Search
from opensearch_dsl import Document, Text, Keyword
from flask import Flask, request
import re
import os
import json
import requests


app = Flask(__name__)

index_name = "indice_1"

#################################### Funciones ####################################

# Para extraer el paper_id del pdf de archive que busquemos
def extraer_arxiv(texto):
    regex = r"arXiv:(\d+\.\d+(?:v\d+)?)"
    match = re.search(regex, texto)
    if match:
        resultado = match.group(1)  # Obtiene el texto coincidente
        resultado_sin_v = resultado.split('v')[0]  # Elimina 'v' y lo que le sigue
        return resultado_sin_v
    else:
        return None 

#--------------------------------------------------------------------------------------

# Para descargarme el pdf correspondiente cuando solo me pasan el id del paper por el input
def descargar_pdf_arxiv(arxiv_id, directorio_destino):
    # Construye la URL del PDF
    url_pdf = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    # Descarga el PDF
    response = requests.get(url_pdf)
    if response.status_code == 200:
        # Guarda el PDF en el directorio especificado
        ruta_pdf = os.path.join(directorio_destino, f"{arxiv_id}.pdf")
        with open(ruta_pdf, 'wb') as f:
            f.write(response.content)
        print(f"PDF descargado correctamente: {ruta_pdf}")
    else:
        print(f"No se pudo descargar el PDF. Código de estado: {response.status_code}")


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
    resultado = client.search(index=index_name, body={"query": {"term": {"paper_id": paper_id}}}, _source=["title"])
    hits = resultado["hits"]["hits"]
    # Verifica si hay resultados
    if hits:
        for hit in hits:
            return hit["_source"]["title"]  # Devuelve el título del documento encontrado
    else:
        return None  # Devuelve None si no se encontró ningún documento con el paper_id dado


################################### Rutas #############################################

# Para recibir el pdf 
@app.route("/uploadPDFText", methods=["POST"])
def upload_pdf_text():
    data = request.json
    pdf_text = data.get('pdfText')
    if pdf_text is None:
        return {"error": "No se proporcionó el texto del PDF"}, 400
    else:
        # Buscar el documento en elasticsearch
        paper_id = extraer_arxiv(pdf_text)
        print(paper_id)
        client = conexion()
        verificar_conexion(client)
        titulo = obtener_titulo_por_paper_id(client, index_name, paper_id)
        if titulo is not None:
            print("Título del documento encontrado:", titulo)
        else:
            print("No se encontró ningún documento con el paper_id dado.")
        
        # Guardar el pdf en un .txt
        with open('pdf_text.txt', 'w') as file:
            file.write(pdf_text)
        return {"message": "Texto del PDF recibido y guardado exitosamente en pdf_text.txt."}

#-------------------------------------------------------------------------------------

# Para recibir el input de la cuarta opcion del accordion
@app.route("/uploadInputText", methods=["POST"])
def upload_input_text():
    data = request.json
    input_text = data.get('inputText')
    if input_text is None:
        return {"error": "No se proporcionó el texto del input"}, 400
    else:
        # Mostrar el texto del input en la terminal
        print("Texto del input recibido:", input_text)
        # Para descargar el pdf correspondiente al id que el usuario ha introducido
        descargar_pdf_arxiv(input_text, "../datos/")
        return {"message": "Texto del input recibido y mostrado en la terminal."}

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
        print('Texto seleccionado:', selected_text)
        return {"message": "Texto seleccionado recibido y mostrado en la terminal."}

#------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
