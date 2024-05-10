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


def limpiar_texto_entrenar(texto):
    # Eliminar secuencias de números y letras seguidos
    texto_limpio = re.sub(r'\b\w+\d+\w*\b', '', texto.lower())
    # Eliminar caracteres no alfanuméricos y convertir a minúsculas
    texto_limpio = re.sub(r'[^\w\s]', '', texto_limpio)
    # Reemplazar múltiples espacios consecutivos por uno solo
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    # Devolver el texto limpio como un solo string
    return texto_limpio.strip()

class ObtenerParrafos(object):
    def __init__(self, directorio_raiz):
        self.directorio_raiz = directorio_raiz

    def __iter__(self):
        for carpeta in os.listdir(self.directorio_raiz):
            carpeta_completa = os.path.join(self.directorio_raiz, carpeta)
            for fjson in os.listdir(carpeta_completa):
                json_completo = os.path.join(carpeta_completa, fjson)
                with open(json_completo, 'r') as f:
                    for line in f:
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

mis_palabras = ObtenerParrafos("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/pruebas_entrenamiento")

model = Word2Vec(min_count=1)

# Construir vocabulario
model.build_vocab(mis_palabras)

# Entrenar el modelo
model.train(mis_palabras, total_examples=model.corpus_count, epochs=model.epochs)

nombre_modelo_bin = "modelo_entrenado.bin"
model.wv.save_word2vec_format(nombre_modelo_bin, binary=True)



