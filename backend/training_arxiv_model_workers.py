
# pip install gensim
import numpy as np
from gensim.models import KeyedVectors
from numpy import dot
from numpy.linalg import norm
import time
import sys
import gensim
from gensim.models import Word2Vec
import os, json, re, spacy
# from text_processor import TextProcessor
# from elasticsearch_client import ElasticsearchClient
import nltk
import argparse

import logging
logging.basicConfig(filename='log_txt_modelo_2_4.log',
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    level=logging.INFO)

nlp = spacy.load('en_core_web_sm')


##################################################################################################

#Ver https://radimrehurek.com/gensim/parsing/preprocessing.html
def limpiar_texto_entrenar(texto):
    # Eliminar secuencias de números y letras seguidosS
    texto_limpio = re.sub(r'\b\w+\d+\w*\b', '', texto.lower())
    # Eliminar caracteres no alfanuméricos y convertir a minúsculas
    texto_limpio = re.sub(r'[^\w\s]', '', texto_limpio)
    # Reemplazar múltiples espacios consecutivos por uno solo
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    # Devolver el texto limpio como un solo string
    return texto_limpio.strip()

#-----------------------------------------

class ObtenerParrafos(object):
    def __init__(self, directorio_raiz, nombre_fichero_salida):
        self.directorio_raiz = directorio_raiz
        self.nombre_fichero_salida = nombre_fichero_salida

        self.carpetas = [os.path.join(self.directorio_raiz, carpeta) for carpeta in os.listdir(self.directorio_raiz)]
        self.jsones = []
        for carpeta in self.carpetas:
            for fjson in os.listdir(carpeta):
                self.jsones.append(os.path.join(carpeta, fjson))

    def __iter__(self):
        # Si el archivo de salida ya existe, se vacía
        if os.path.exists(self.nombre_fichero_salida):
            open(self.nombre_fichero_salida, 'w', encoding='utf-8').close()

        nJsones = len(self.jsones)
        i = 0
        with open(self.nombre_fichero_salida, 'a', encoding='utf-8') as file:
            for fjson in self.jsones:
                i += 1
                print("(%d/%d) %s" % (i, nJsones, fjson))
                with open(fjson, 'r', encoding='utf-8') as f:
                    for line in f:
                        line_json = json.loads(line)
                        body = line_json["body_text"]
                        for obj in body:
                            texto = limpiar_texto_entrenar(obj["text"])
                            texto_procesado = nlp(texto)
                            obtained_text_words = [token.text for token in texto_procesado if token.is_alpha]
                            # Escribe las palabras alfabéticas de un body_text en una línea del archivo
                            file.write(' '.join(obtained_text_words))
                        file.write('\n')
        yield None

#------------------------------------
def main_crear_txt(dir, ficheroSalida):
    start_time = time.time()
    mis_palabras = ObtenerParrafos(dir, ficheroSalida)
    for _ in mis_palabras:
        pass
    end_time = time.time()
    elapsed_time = time.time() - start_time
    logging.info("Tiempo transcurrido durante la creación del archivo: %s segundos", elapsed_time)

#------------------------------------

def leer_documentos(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as file:
        documentos = [line.strip().split() for line in file.readlines()]
    return documentos

#------------------------------------

def main_workers(nombre_archivo):
    documentos = leer_documentos(nombre_archivo)

    # Paso 2: Configurar y entrenar el modelo Word2Vec
    model = Word2Vec(vector_size=200,  # Cambiado a 200
                    window=5,
                    hs=0,  # 0=negative sampling
                    sg=1,  # 1=skip-gram
                    shrink_windows=True,  # draw window size from uniform [1, window]
                    negative=10,
                    ns_exponent=0.75,
                    min_count=3,
                    workers=8,  # Número de workers
                    seed=1,
                    epochs=2)

    # Construir el vocabulario
    model.build_vocab(documentos, progress_per=10000)

    # Entrenar el modelo
    start_time = time.time()
    model.train(documentos, total_examples=model.corpus_count, epochs=model.epochs, report_delay=1)
    end_time = time.time()

    # Guardar el modelo entrenado en formato binario
    fichModeloEntrenado = 'modelo_entrenado.bin'
    model.wv.save_word2vec_format(fichModeloEntrenado, binary=True)

    # Imprimir el tiempo transcurrido durante el entrenamiento
    elapsed_time = end_time - start_time
    print("Tiempo transcurrido durante el entrenamiento:", elapsed_time, "segundos")

#--------------------------------------
primer_txt = "./modelo_2_4_carpeta"
entrenado_1 = "modelo_entrenado_2_4.bin"

segundo_txt = "./modelo_18_19_20_carpeta"
entrenado_2 = "modelo_entrenado_2_4_18_19_20.bin"

tercer_txt = "./modelo_21_carpeta"
entrenado_3 = "modelo_entrenado_2_4_18_19_20_21.bin"

cuarto_txt = "./modelo_22_carpeta"
entrenado_4 = "modelo_entrenado_2_4_18_19_20_21_22.bin"

main_crear_txt(primer_txt, "txt_modelo_2_4.txt")
# main_workers("salida_mediana.txt")

#print("Rentrenando modelo %s ..."%(entrenado_1))
#main_reentrenar(dir_2,entrenado_1,entrenado_2)

# print("Rentrenando modelo %s ..."%(entrenado_2))
# main_reentrenar(dir_3,entrenado_2,entrenado_3)

# print("Reentrenando modelo %s ..."%(entrenado_3))
# main_reentrenar(dir_4,entrenado_3,entrenado_4)
