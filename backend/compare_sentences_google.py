"""-------------------------------------------------------------------------
Nombre del archivo: compare_sentences.py
Autora:             Paula Ezpeleta Castrillo
Fecha de creación:  15/05/2024
Descripción:        Codigo necesario para la comparación de similitud entre textos usando un modelo entrenado de Google
-------------------------------------------------------------------------"""

# pip install gensim
import numpy as np
from gensim.models import KeyedVectors
from numpy import dot
from numpy.linalg import norm
import time
import sys
import random

from sklearn.metrics.pairwise import cosine_similarity

#-----------------------------------
# valores globales
fichModel = '../datos/GoogleNews-vectors-negative300.bin'
model = KeyedVectors.load_word2vec_format(fichModel, binary=True)

print("(w,dim): (%d,%d)" % (model.vectors.shape[0], model.vectors.shape[1]))
# contains the list of all unique words in pre-trained word2vec vectors
vocabulary = list(model.key_to_index.keys())
#-----------------------------------
def getInput():
    sys.stdout.write('--> ')
    return input()
#-----------------------------------
# https://stackoverflow.com/questions/8897593/how-to-compute-the-similarity-between-two-text-documents

def obtener_similitud_entre_cita_y_articulo(tokens_cita, tokens_articulo, modelo, vocabulary):
    # Obtener vectores de palabras para la cita
    vectores_cita = []
    numero_cita_desconocidas = 0
    numero_vector_desconocidas = 0
    numero_cita_conocidas = 0
    numero_vector_conocidas = 0
    vectores_cita = []
    for token in tokens_cita:
        try:
            numero_cita_conocidas += 1
            vector = modelo[token]  # Aquí se corrige la línea
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
            vector = modelo[token]  # Aquí se corrige la línea
            vectores_articulo.append(vector)
        except KeyError:
            numero_vector_desconocidas += 1
            print("Palabra desconocida: %s" % token)
            # Manejar palabras desconocidas
            pass

    # Promediar vectores de palabras para obtener representaciones vectoriales de la cita y el artículo
    representacion_cita = np.mean(vectores_cita, axis=0)
    representacion_articulo = np.mean(vectores_articulo, axis=0)
    
    # Ahora se compara la similitud entre las representaciones vectoriales de la cita y el artículo, usando el coseno
    similitud = dot(representacion_cita, representacion_articulo) / (norm(representacion_cita) * norm(representacion_articulo))
    print("Palabras conocidas en la cita: %d" % numero_cita_conocidas)
    print("Palabras desconocidas en la cita: %d" % numero_cita_desconocidas)
    print("Palabras totales en la cita: %d" % len(tokens_cita))
    print("Palabras conocidas en el artículo: %d" % numero_vector_conocidas)
    print("Palabras desconocidas en el artículo: %d" % numero_vector_desconocidas)
    print("Palabras totales en el artículo: %d" % len(tokens_articulo))
    print("Porcentaje de desconocidas en la cita: %f" % (numero_cita_desconocidas / len(tokens_cita)))
    print("Porcentaje de desconocidas en el artículo: %f" % (numero_vector_desconocidas / len(tokens_articulo)))
    return similitud

#-----------------------------------
def main_1(model):
    pal = getInput()
    while pal:
        if pal in vocabulary:
            print(model.most_similar(positive=[pal]))
        pal = getInput()
#----------------------------------------------------------
def show_results(scores):
    for s in scores:
        print("(%d,%d): %f" % (s[0][0], s[0][1], s[1]))
#-----------------------------------
def main_2(model):
    s1 = ['In this chapter we introduce mechanisms for declaring new types and classes in Haskell. We start with three approaches to declaring types, then consider recursive types, show how to declare classes and their instances, and conclude by developing a tautology checker and an abstract machine']
     
    s2 = [
        'In this chapter, we explore methods for defining new types and classes in Haskell. We begin with three techniques for declaring types, followed by a discussion on recursive types. Next, we demonstrate how to declare classes and their instances. Finally, we conclude by creating a tautology checker and an abstract machine',
        'He says they are showing how to declare classes and instances',
        'They do not show how to declare classes and instances',
        'In this chapter we present mechanisms for declaring new classes',
        'It seems the authors propose the use of Haskell',
        'It seems the authors are against the use of Haskell',
        'This is bullshit'
    ]
    scores = {}
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
