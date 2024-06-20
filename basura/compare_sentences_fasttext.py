"""-------------------------------------------------------------------------
Nombre del archivo: compare_sentences_fasttext.py
Autora:             Paula Ezpeleta Castrillo
Fecha de creación:  15/05/2024
Descripción:        Codigo necesario para la comparación de similitud entre textos usando un modelo entrenado de fasttext
-------------------------------------------------------------------------"""


import fasttext
import numpy as np
from numpy import dot
from numpy.linalg import norm
import sys
import os, json, re, spacy
import random
from sklearn.metrics.pairwise import cosine_similarity

#-----------------------------------

# valores globales
fichModel = '../datos/cc.en.300.bin'
model = fasttext.load_model(fichModel)
print(f"Dimensión del modelo: {model.get_dimension()}")

# contains the list of all unique words in pre-trained fasttext vectors
def get_vocabulary(model):
    return set(model.get_words())

vocabulary = get_vocabulary(model)

#-----------------------------------

def getInput():
    sys.stdout.write('--> ')
    return input()

#-----------------------------------

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
            vector = modelo.get_word_vector(token)
            vectores_cita.append(vector)
        except KeyError:
            numero_cita_desconocidas += 1
            print("Palabra desconocida")
            # Manejar palabras desconocidas
            pass

    # Obtener vectores de palabras para el artículo
    vectores_articulo = []
    for token in tokens_articulo:
        try:
            numero_vector_conocidas += 1
            vector = modelo.get_word_vector(token)
            vectores_articulo.append(vector)
        except KeyError:
            # Manejar palabras desconocidas
            numero_vector_desconocidas += 1
            print("Palabra desconocida")
            pass

    # Promediar vectores de palabras para obtener representaciones vectoriales de la cita y el artículo
    representacion_cita = np.mean(vectores_cita, axis=0)
    representacion_articulo = np.mean(vectores_articulo, axis=0)
    
    # Ahora se compara la similitud entre las representaciones vectoriales de la cita y el artículo, usando el coseno
    similitud = dot(representacion_cita, representacion_articulo) / (norm(representacion_cita) * norm(representacion_articulo))
    print("Palabras conocidas en la cita: %d" % numero_cita_conocidas)
    print("Palabras totales en la cita: %d" % len(tokens_cita))
    print("Palabras conocidas en el artículo: %d" % numero_vector_conocidas)
    print("Palabras totales en el artículo: %d" % len(tokens_articulo))
    print("Porcentaje de desconocidas en la cita: %f" % (numero_cita_desconocidas / len(tokens_cita)))
    print("Porcentaje de desconocidas en el artículo: %f" % (numero_vector_desconocidas / len(tokens_articulo)))
    return similitud

#-----------------------------------

def main_1(model):
    pal = getInput()
    while not pal == "":
        if pal in vocabulary:
            print(model.get_nearest_neighbors(pal))
        pal = getInput()

#----------------------------------------------------------

def show_results(scores):
    for i in range(len(scores)):
        s = scores[i]
        print("(%d,%d): %f"%(s[0][0],s[0][1],s[1]))

#-----------------------------------

def main_2(model):
    s1 = ['In this chapter we introduce mechanisms for declaring new types and classes in Haskell. We start with three approaches to declaring types, then consider recursive types, show how to declare classes and their instances, and conclude by developing a tautology checker and an abstract machine sdfkhsirufgis']
    
    s2 = [
        'In this chapter, we explore methods for defining new types and classes in Haskell. We begin with three techniques for declaring types, followed by a discussion on recursive types. Next, we demonstrate how to declare classes and their instances. Finally, we conclude by creating a tautology checker and an abstract machine',
        'He says they are showing how to declare classes and instances',
        'They do not show how to declare classes and instances',
        'In this chapter we present mechanisms for declaring new classes',
        'It seems the authors propose the use of Haskell',
        'It seems the authors are against the use of Haskell',
        'This is bullshit'
    ]
    scores = dict()
    for i in range(len(s1)):
        for j in range(len(s2)):
            t1 = s1[i].split(' ')
            t2 = s2[j].split(' ')
            sim = obtener_similitud_entre_cita_y_articulo(t1, t2, model, vocabulary)
            scores[(i, j)] = sim
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    show_results(sorted_scores)
    
#-----------------------------------

def main_3():
    si, no, palsExtra = countWords(vocabulary)
    print("Comunes: %d, Extra: %d" % (si, no))

    lExtra = list(palsExtra)
    for i in range(1000):
        sys.stdout.write("%s " % (random.choice(lExtra)))
    print('')

#-----------------------------------

if __name__ == '__main__':
    #main_3()
    main_2(model)
