"""
-------------------------------------------------------------------------
Nombre del archivo: compare_sentences.py
Autora:             Paula Ezpeleta Castrillo
Fecha de creación:  15/05/2024
Descripción:        Módulo correspondiente a todas las operaciones a realizar con pdf's
-------------------------------------------------------------------------"""

import os
import re
import requests
import numpy as np
from gensim.models import KeyedVectors
from numpy import dot
from numpy.linalg import norm

class ModelProcessor:
    fichModel = '../datos/GoogleNews-vectors-negative300.bin'
    model = KeyedVectors.load_word2vec_format(fichModel, binary=True)

    # print("(w,dim): (%d,%d)" % (model.vectors.shape[0], model.vectors.shape[1]))
    # Contains the list of all unique words in pre-trained word2vec vectors
    vocabulary = list(model.key_to_index.keys())

    def __init__(self):
        pass

    @staticmethod
    def obtener_similitud_entre_cita_y_articulo(tokens_cita, tokens_articulo, modelo, vocabulary):
        # Obtener vectores de palabras para la cita
        vectores_cita = []
        numero_cita_desconocidas = 0
        numero_vector_desconocidas = 0
        numero_cita_conocidas = 0
        numero_vector_conocidas = 0

        for token in tokens_cita:
            try:
                numero_cita_conocidas += 1
                vector = modelo[token]
                vectores_cita.append(vector)
            except KeyError:
                numero_cita_desconocidas += 1
                # Manejar palabras desconocidas
                pass

        # Obtener vectores de palabras para el artículo
        vectores_articulo = []
        for token in tokens_articulo:
            try:
                numero_vector_conocidas += 1
                vector = modelo[token]
                vectores_articulo.append(vector)
            except KeyError:
                numero_vector_desconocidas += 1
                # print("Palabra desconocida: %s" % token)
                # Manejar palabras desconocidas
                pass

        # Promediar vectores de palabras para obtener representaciones vectoriales de la cita y el artículo
        representacion_cita = np.mean(vectores_cita, axis=0)
        representacion_articulo = np.mean(vectores_articulo, axis=0)

        # Comparar la similitud entre las representaciones vectoriales de la cita y el artículo, usando el coseno
        similitud = dot(representacion_cita, representacion_articulo) / (norm(representacion_cita) * norm(representacion_articulo))

        # print("Palabras conocidas en la cita: %d" % numero_cita_conocidas)
        # print("Palabras desconocidas en la cita: %d" % numero_cita_desconocidas)
        # print("Palabras totales en la cita: %d" % len(tokens_cita))
        # print("Palabras conocidas en el artículo: %d" % numero_vector_conocidas)
        # print("Palabras desconocidas en el artículo: %d" % numero_vector_desconocidas)
        # print("Palabras totales en el artículo: %d" % len(tokens_articulo))
        # print("Porcentaje de desconocidas en la cita: %f" % (numero_cita_desconocidas / len(tokens_cita)))
        # print("Porcentaje de desconocidas en el artículo: %f" % (numero_vector_desconocidas / len(tokens_articulo)))

        return similitud
