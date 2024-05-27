
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
import random

from sklearn.metrics.pairwise import cosine_similarity
#-----------------------------------
# valores globales
fichModel = '../datos/1_modelo_entrenado_2_4_18_19_20_21_22.bin'
# fichModel = '/home/paula/TFG/pruebas/docs/GoogleNews-vectors-negative300.bin'

model = gensim.models.Word2Vec.load(fichModel)
#para modelo binario de Google
# model = KeyedVectors.load_word2vec_format(fichModel, binary=True)


print("(w,dim): (%d,%d)"%(model.wv.vectors.shape))
# contains the list of all unique words in pre-trained word2vec vectors
vocabulary = list(model.wv.key_to_index.keys())
#-----------------------------------
def getInput():
    sys.stdout.write('--> ')
    return input()
#-----------------------------------
#dict: 104335, #words: 771416
#comunes: 40920
#Si: 40920, No: 730496
def countWords(vocabulary):
    dict = '/usr/share/dict/words'
    si = 0
    no = 0
    dictWords = []
    with open("/usr/share/dict/words", "r") as fDict:
        dictWords = fDict.read().split('\n')

    map(str.lower,dictWords)
    
    map(str.lower,vocabulary)
    lenDict = len(dictWords)
    lenVocab = len(vocabulary)
    print("#dict: %d, #words model: %d"%(lenDict,lenVocab))

    dictWords = set(dictWords)
    dictVocabulary = set(vocabulary)
    lenComunes = len(list(dictWords.intersection(dictVocabulary)))

    palsExtra = dictVocabulary.difference(dictWords)
    
    return lenComunes, lenVocab-lenComunes, palsExtra
#-----------------------------------
def main_1(model):
    pal = getInput()
    while not pal == "":
        if pal in vocabulary:
            print(model.wv.most_similar(positive=[pal]))
        pal = getInput()
#-----------------------------------
def main_2():
    num_pal = 100
    si,no,palsExtra = countWords(vocabulary)
    print("Comunes: %d, Extra: %d"%(si,no))

    lExtra = list(palsExtra)
    for i in range(num_pal):
         sys.stdout.write("%s "%(random.choice((lExtra))))
    print('')
#-----------------------------------
if __name__ == '__main__':
    # main_1(model)
    main_2()

