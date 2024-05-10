# pip install gensim
import numpy as np
from gensim.models import KeyedVectors
from numpy import dot
from numpy.linalg import norm
import time
import sys
from gensim.models import Word2Vec
import os, json, re, spacy
from text_processor import TextProcessor
from elasticsearch_client import ElasticsearchClient
import nltk


nlp = spacy.load('en_core_web_sm')

lista_1 = ['02', '93', '00', '98', '01', '97', '03', '04', '05', '07', '06', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18']
lista_2 = ['19', '20']
lista_3 = ['21']
lista_4 = ['22']
lista_prueba = ['02', '93', '00', '98', '01']

modelo_google = '../datos/GoogleNews-vectors-negative300.bin'

# def obtener_similitud_entre_cita_y_articulo(tokens_cita, tokens_articulo, nombre_modelo_preentrenado):
#     # Cargar modelo pre-entrenado de Word2Vec
#     modelo_word2vec = KeyedVectors.load_word2vec_format(nombre_modelo_preentrenado, binary=True)

#     # Obtener vectores de palabras para la cita
#     vectores_cita = []
#     for token in tokens_cita:
#         try:
#             vector = modelo_word2vec[token]
#             vectores_cita.append(vector)
#         except KeyError:
#             # Manejar palabras desconocidas
#             pass

#     # Obtener vectores de palabras para el artículo
#     vectores_articulo = []
#     for token in tokens_articulo:
#         try:
#             vector = modelo_word2vec[token]
#             vectores_articulo.append(vector)
#         except KeyError:
#             # Manejar palabras desconocidas
#             pass

#     # Promediar vectores de palabras para obtener representaciones vectoriales de la cita y el artículo
#     representacion_cita = np.mean(vectores_cita, axis=0)
#     representacion_articulo = np.mean(vectores_articulo, axis=0)

#     # Ahora se compara la similitud entre las representaciones vectoriales de la cita y el artículo, usando el coseno
#     similitud = dot(representacion_cita, representacion_articulo) / (norm(representacion_cita) * norm(representacion_articulo))
#     print("Similitud entre la cita y el artículo:", similitud)

# def calcular_tam_lista_de_listas(lista_de_listas):
#     tam = 0
#     for e in lista_de_listas:
#         tam += sum([len(palabra) for palabra in e])
#     return tam



# def entrenar_modelo_word2vec(lista_listas, nombre_modelo_bin):

#     # Suponiendo que 'documentos_preprocesados' es tu lista de listas con palabras preprocesadas de tus documentos
#     modelo_word2vec = Word2Vec(sentences=lista_listas, vector_size=100, window=5, min_count=1, sg=0)

#     # Entrenar el modelo
#     modelo_word2vec.train(lista_listas, total_examples=len(lista_listas), epochs=10)

#     # Guardar el modelo en un archivo .bin
#     modelo_word2vec.wv.save_word2vec_format(nombre_modelo_bin, binary=True)

#-----------------------------------------------------------------
##############Funciones para entrenar el modelo con todos los json de las carpetas###############

class ObtenerParrafos(object):
    def __init__(self, jsonfile):
        self.jsonfile = jsonfile

    def __iter__(self):
        try:
            for line in open(self.jsonfile, mode='rt', encoding='UTF-8'):
                line_json = json.loads(line)
                # Extrae los campos a indexar
                body = line_json["body_text"]
                for obj in body:
                    # cojo el parrafo, que sera de tipo string
                    texto = limpiar_texto_entrenar(obj["text"])
                    # Procesar el texto y la cita con el modelo de spaCy
                    texto_procesado = nlp(texto)
                    # Obtener todas las palabras alfabéticas detectadas por spaCy
                    obtained_text_words = [token.text for token in texto_procesado if token.is_alpha]
                    # print(obtained_text_words[0])
                    yield obtained_text_words
        except Exception:
            print ('Failed reading file: ')
            print (self.jsonfile)


class ObtenerParrafosDeJSONS(object):
    # carpeta es el path completo
    def __init__(self, carpeta):
        self.carpeta = carpeta

    def __iter__(self):
        try:
            for fjson in os.listdir(carpeta_completa):
                yield ObtenerParrafos(os.path.join(carpeta_completa, fjson))
        except Exception:
            print ('Failed reading file: ')
            print (self.carpeta)

class ObtenerParrafosDeDirectorio(object):
    # carpeta es el path completo
    def __init__(self, nombre_directorio):
        self.nombre_directorio = nombre_directorio

    def __iter__(self):
        try:
            for carpeta in os.listdir(nombre_directorio):
                yield ObtenerParrafosDeJSONS(os.path.join(nombre_directorio, carpeta))
        except Exception:
            print ('Failed reading directory: ')
            print (self.nombre_directorio)
            

mis_palabras = ObtenerParrafosDeDirectorio("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/unarXive_230324_open_subset")

# Iterar sobre mis_palabras para obtener las palabras de todos los archivos JSON
palabras = []
for parrafos_jsons in mis_palabras:
    for palabras_parrafo in parrafos_jsons:
        palabras.extend(palabras_parrafo)

# Crear modelo Word2Vec
model = Word2Vec(min_count=1)

# Construir vocabulario
model.build_vocab([palabras])

# Entrenar el modelo
model.train([palabras], total_examples=model.corpus_count, epochs=model.epochs)

# def entrenar_modelo_con_documentos_carpetas(lista):
#     for carpeta_pequeña in lista:
#         # Construir la ruta completa a la carpeta
#         carpeta_completa = os.path.join("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/unarXive_230324_open_subset", carpeta_pequeña)
#         files = [f for f in os.listdir(carpeta_completa)]
#         start_time = time.time()
#         print("Carpeta completa: ", carpeta_completa)
#         for f_json in files:
#             print("Nombre json: ", f_json)
#             nombre = os.path.join(carpeta_completa, f_json)
#             print("Nombre completo: ", str(nombre))
#             for parrafo in  ObtenerParrafos(nombre):
#                 print(parrafo[0])
#             # entrenar_con_cuerpo_json(nombre)
#     print("--- %s seconds ---" % (time.time() - start_time))
            
    
#-----------------------------------------------------------------

# def entrenar_con_cuerpo_json(json_file):
#     with open(json_file, "r") as f:
#         datos = f.readlines()
#         # Itera sobre cada línea del archivo JSONL
#         for line in datos:
#             # Carga el JSON de la línea actual
#             line_json = json.loads(line)
#             # Extrae los campos a indexar
#             body = line_json["body_text"]
#             for obj in body:
#                 # cojo el parrafo, que sera de tipo string
#                 texto = limpiar_texto_entrenar(obj["text"])
#                 # Procesar el texto y la cita con el modelo de spaCy
#                 texto_procesado = nlp(texto)
#                 # Obtener todas las palabras alfabéticas detectadas por spaCy
#                 obtained_text_words = [token.text for token in texto_procesado if token.is_alpha]
#                 print(type(obtained_text_words))
#                 yield obtained_text_words
                


#-----------------------------------------------------------------


def limpiar_texto_entrenar(texto):
    # Eliminar secuencias de números y letras seguidos
    texto_limpio = re.sub(r'\b\w+\d+\w*\b', '', texto.lower())
    # Eliminar caracteres no alfanuméricos y convertir a minúsculas
    texto_limpio = re.sub(r'[^\w\s]', '', texto_limpio)
    # Reemplazar múltiples espacios consecutivos por uno solo
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    # Devolver el texto limpio como un solo string
    return texto_limpio.strip()




# def main():
#     # client = ElasticsearchClient()
#     # lista_tokens_texto = client.obtener_tokens_cuerpo("indice_1","1203.1858", "../datos/archivo.txt")
#     # texto_cita_limpio = TextProcessor.limpiar_texto(" Finally, our conclusions and future work appear in Section 6 methods [18 ]) and learned (e.g., distributional measures that esti-mate semantic relatedness between terms using a multidimensional space model to correlate words and textual contexts [ 25])")
#     # texto_cita_limpio = ' '.join(texto_cita_limpio)
#     # lista_tokens_cita = TextProcessor.obtain_list_english_words_from_body(texto_cita_limpio)
#     # obtener_similitud_entre_cita_y_articulo(lista_tokens_cita, lista_tokens_texto)
#     # #Similitud entre la cita y el artículo: 0.85897756
#     client = ElasticsearchClient()
#     start_time = time.perf_counter()
#     documentos_principio, documentos_final = client.obtener_paper_ids("indice_1")
#     print("Primeros 10 documentos:", documentos_principio)
#     print("Últimos 10 documentos:", documentos_final)
#     print("longitud primeros 10 documentos:", len(documentos_principio))
#     print("longitud últimos 10 documentos:", len(documentos_final))
#     tokens_documentos = []
#     # Obtener tokens para los primeros 10 documentos
#     for documento in documentos_principio:
#         tokens_documento = client.obtener_tokens_cuerpo("indice_1", documento, "tokens10primeros.txt")
#         tokens_documentos.append(tokens_documento)

#     # Obtener tokens para los últimos 10 documentos
#     for documento in documentos_final:
#         tokens_documento = client.obtener_tokens_cuerpo("indice_1", documento, "tokens10ultimos.txt")
#         tokens_documentos.append(tokens_documento)

#     print("Tokens de todos los documentos:", tokens_documentos)
#     print("Longitud de lista de listas:", len(tokens_documentos))
#     end_time = time.perf_counter()
#     tamanio_bytes = sys.getsizeof(tokens_documentos)
#     print("Tamaño de la lista en bytes:", tamanio_bytes, "bytes")
#     print("tiempo dedicado:", end_time - start_time, "segundos")
#     print("tamaño: %d "%(calcular_tam_lista_de_listas(tokens_documentos)))
#     entrenar_modelo_word2vec(tokens_documentos, 'modelo_entrenado_4_documentos.bin') # Entrenar modelo Word2Vec con los tokens de los documentos
#     #-------------------
#     lista_tokens_texto = client.obtener_tokens_cuerpo("indice_1","1203.1858", "../datos/archivo.txt")
#     texto_cita_limpio = TextProcessor.limpiar_texto(" kk de la vaca es una mierda noseque")
#     texto_cita_limpio = ' '.join(texto_cita_limpio)
#     lista_tokens_cita = TextProcessor.obtain_list_english_words_from_body(texto_cita_limpio)
#     obtener_similitud_entre_cita_y_articulo(lista_tokens_cita, lista_tokens_texto, 'modelo_entrenado_4_documentos.bin')



# main()


# entrenar_modelo_con_documentos_carpetas(lista_prueba)