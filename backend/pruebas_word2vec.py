# pip install gensim
import numpy as np
from gensim.models import KeyedVectors
from numpy import dot
from numpy.linalg import norm

from text_processor import TextProcessor
from elasticsearch_client import ElasticsearchClient

def obtener_similitud_entre_cita_y_articulo(tokens_cita, tokens_articulo):
    # Cargar modelo pre-entrenado de Word2Vec
    modelo_word2vec = KeyedVectors.load_word2vec_format('../datos/GoogleNews-vectors-negative300.bin', binary=True)

    # Obtener vectores de palabras para la cita
    vectores_cita = []
    for token in tokens_cita:
        try:
            vector = modelo_word2vec[token]
            vectores_cita.append(vector)
        except KeyError:
            # Manejar palabras desconocidas
            pass

    # Obtener vectores de palabras para el artículo
    vectores_articulo = []
    for token in tokens_articulo:
        try:
            vector = modelo_word2vec[token]
            vectores_articulo.append(vector)
        except KeyError:
            # Manejar palabras desconocidas
            pass

    # Promediar vectores de palabras para obtener representaciones vectoriales de la cita y el artículo
    representacion_cita = np.mean(vectores_cita, axis=0)
    representacion_articulo = np.mean(vectores_articulo, axis=0)

    # Ahora se compara la similitud entre las representaciones vectoriales de la cita y el artículo, usando el coseno
    similitud = dot(representacion_cita, representacion_articulo) / (norm(representacion_cita) * norm(representacion_articulo))
    print("Similitud entre la cita y el artículo:", similitud)



def main():
    client = ElasticsearchClient()
    lista_tokens_texto = client.obtener_tokens_cuerpo("indice_1","1203.1858", "../datos/archivo.txt")
    texto_cita_limpio = TextProcessor.limpiar_texto(" Finally, our conclusions and future work appear in Section 6 methods [18 ]) and learned (e.g., distributional measures that esti-mate semantic relatedness between terms using a multidimensional space model to correlate words and textual contexts [ 25])")
    texto_cita_limpio = ' '.join(texto_cita_limpio)
    lista_tokens_cita = TextProcessor.obtain_list_english_words_from_body(texto_cita_limpio)
    obtener_similitud_entre_cita_y_articulo(lista_tokens_cita, lista_tokens_texto)
    #Similitud entre la cita y el artículo: 0.85897756

main()
