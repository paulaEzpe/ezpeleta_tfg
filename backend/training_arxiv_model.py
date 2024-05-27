
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
logging.basicConfig(filename='log_22.log',
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

class ObtenerParrafos(object):
    def __init__(self, directorio_raiz):
        self.directorio_raiz = directorio_raiz

        self.carpetas = [os.path.join(self.directorio_raiz, carpeta) for carpeta in os.listdir(self.directorio_raiz)]
        #print('carpetas: ' + str(self.carpetas))
        self.jsones = []
        for carpeta in self.carpetas:
            for fjson in os.listdir(carpeta):
                self.jsones.append(os.path.join(carpeta, fjson))
        #print('jsones: ' + str(self.jsones))

    def __iter__(self):
        nJsones = len(self.jsones)
        i = 0
        for fjson in self.jsones:
            i = i + 1
            print("(%d/%d) %s"%(i,nJsones,fjson))
            with open(fjson, 'r') as f:
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
#-----------------------------------------------
def main_reentrenar(dir,fichModeloEntrenado,fichModeloReentrenado):
    mis_palabras = ObtenerParrafos(dir)
    # Cargar el modelo existente

    model = Word2Vec.load(fichModeloEntrenado)
    # Actualizar el vocabulario y continuar el entrenamiento
    model.build_vocab(mis_palabras, update=True, progress_per=10000)
    start_time = time.time()
    model.train(mis_palabras, total_examples=model.corpus_count, epochs=model.epochs, report_delay=1)
    end_time = time.time()

    model.save(fichModeloReentrenado)
    elapsed_time = time.time() - start_time
    print("Tiempo transcurrido durante el entrenamiento:", elapsed_time, "segundos")

#------------------------------------
def main_entrenar(dir,fichModeloEntrenado):
    mis_palabras = ObtenerParrafos(dir)
    model = gensim.models.Word2Vec(vector_size=50,
                        window=5,
                        hs=0, #0=negative sampling
                        sg=1, #1=skip-gram
                        shrink_windows=True, #draw window size from uniform [1,window]
                        negative=10,
                        ns_exponent=0.75,
                        min_count=3,
                        workers=8,
                        seed=1,
                        epochs=2)
    model.build_vocab(mis_palabras, progress_per=10000)
    start_time = time.time()
    model.train(mis_palabras, total_examples=model.corpus_count, epochs=model.epochs, report_delay=1)
    end_time = time.time()

    # model.wv.save_word2vec_format(nombre_modelo_bin, binary=True)
    model.save(fichModeloEntrenado)
    elapsed_time = time.time() - start_time
    print("Tiempo transcurrido durante el entrenamiento:", elapsed_time, "segundos")
#--------------------------------------
dir_1 = "./modelo_2_4_carpeta"
entrenado_1 = "modelo_entrenado_2_4.bin"

dir_2 = "./modelo_18_19_20_carpeta"
entrenado_2 = "modelo_entrenado_2_4_18_19_20.bin"

dir_3 = "./modelo_21_carpeta"
entrenado_3 = "modelo_entrenado_2_4_18_19_20_21.bin"

dir_4 = "./modelo_22_carpeta"
entrenado_4 = "modelo_entrenado_2_4_18_19_20_21_22.bin"

# print("Entrenando modelo %s ..."%(dir_1))
# main_entrenar(dir_1,entrenado_1)

#print("Rentrenando modelo %s ..."%(entrenado_1))
#main_reentrenar(dir_2,entrenado_1,entrenado_2)

# print("Rentrenando modelo %s ..."%(entrenado_2))
# main_reentrenar(dir_3,entrenado_2,entrenado_3)

# print("Reentrenando modelo %s ..."%(entrenado_3))
# main_reentrenar(dir_4,entrenado_3,entrenado_4)
