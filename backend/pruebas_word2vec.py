# pip install gensim
import numpy as np
from gensim.models import KeyedVectors
from numpy import dot
from numpy.linalg import norm
import time
import sys
from gensim.models import Word2Vec

from text_processor import TextProcessor
from elasticsearch_client import ElasticsearchClient

modelo_google = '../datos/GoogleNews-vectors-negative300.bin'

def obtener_similitud_entre_cita_y_articulo(tokens_cita, tokens_articulo, nombre_modelo_preentrenado):
    # Cargar modelo pre-entrenado de Word2Vec
    modelo_word2vec = KeyedVectors.load_word2vec_format(nombre_modelo_preentrenado, binary=True)

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

def calcular_tam_lista_de_listas(lista_de_listas):
    tam = 0
    for e in lista_de_listas:
        tam += sum([len(palabra) for palabra in e])
    return tam



def entrenar_modelo_word2vec(lista_listas, nombre_modelo_bin):

    # Suponiendo que 'documentos_preprocesados' es tu lista de listas con palabras preprocesadas de tus documentos
    modelo_word2vec = Word2Vec(sentences=lista_listas, vector_size=100, window=5, min_count=1, sg=0)

    # Entrenar el modelo
    modelo_word2vec.train(lista_listas, total_examples=len(lista_listas), epochs=10)

    # Guardar el modelo en un archivo .bin
    modelo_word2vec.wv.save_word2vec_format(nombre_modelo_bin, binary=True)



def main():
    # client = ElasticsearchClient()
    # lista_tokens_texto = client.obtener_tokens_cuerpo("indice_1","1203.1858", "../datos/archivo.txt")
    # texto_cita_limpio = TextProcessor.limpiar_texto(" Finally, our conclusions and future work appear in Section 6 methods [18 ]) and learned (e.g., distributional measures that esti-mate semantic relatedness between terms using a multidimensional space model to correlate words and textual contexts [ 25])")
    # texto_cita_limpio = ' '.join(texto_cita_limpio)
    # lista_tokens_cita = TextProcessor.obtain_list_english_words_from_body(texto_cita_limpio)
    # obtener_similitud_entre_cita_y_articulo(lista_tokens_cita, lista_tokens_texto)
    # #Similitud entre la cita y el artículo: 0.85897756
    client = ElasticsearchClient()
    start_time = time.perf_counter()
    documentos_principio, documentos_final = client.obtener_paper_ids("indice_1")
    print("Primeros 10 documentos:", documentos_principio)
    print("Últimos 10 documentos:", documentos_final)
    print("longitud primeros 10 documentos:", len(documentos_principio))
    print("longitud últimos 10 documentos:", len(documentos_final))
    tokens_documentos = []
    # Obtener tokens para los primeros 10 documentos
    for documento in documentos_principio:
        tokens_documento = client.obtener_tokens_cuerpo("indice_1", documento, "tokens10primeros.txt")
        tokens_documentos.append(tokens_documento)

    # Obtener tokens para los últimos 10 documentos
    for documento in documentos_final:
        tokens_documento = client.obtener_tokens_cuerpo("indice_1", documento, "tokens10ultimos.txt")
        tokens_documentos.append(tokens_documento)

    print("Tokens de todos los documentos:", tokens_documentos)
    print("Longitud de lista de listas:", len(tokens_documentos))
    end_time = time.perf_counter()
    tamanio_bytes = sys.getsizeof(tokens_documentos)
    print("Tamaño de la lista en bytes:", tamanio_bytes, "bytes")
    print("tiempo dedicado:", end_time - start_time, "segundos")
    print("tamaño: %d "%(calcular_tam_lista_de_listas(tokens_documentos)))
    entrenar_modelo_word2vec(tokens_documentos, 'modelo_entrenado_4_documentos.bin') # Entrenar modelo Word2Vec con los tokens de los documentos
    #-------------------
    lista_tokens_texto = client.obtener_tokens_cuerpo("indice_1","1203.1858", "../datos/archivo.txt")
    texto_cita_limpio = TextProcessor.limpiar_texto(" kk de la vaca es una mierda noseque")
    texto_cita_limpio = ' '.join(texto_cita_limpio)
    lista_tokens_cita = TextProcessor.obtain_list_english_words_from_body(texto_cita_limpio)
    obtener_similitud_entre_cita_y_articulo(lista_tokens_cita, lista_tokens_texto, 'modelo_entrenado_4_documentos.bin')



main()
