import logging
from gensim.models import KeyedVectors
import fasttext
import time
from gensim.models import Word2Vec

def load_model(fichModel):
    try:
        # Intenta cargar el modelo con fasttext
        model = fasttext.load_model(fichModel)
    except Exception as e:
        logging.error(f"Error al cargar el modelo con load: {e}")
        try:
            # Si falla, intenta cargar el modelo con KeyedVectors
            model = KeyedVectors.load_word2vec_format(fichModel, binary=True)
        except Exception as e:
            logging.error(f"Error al cargar el modelo con KeyedVectors: {e}")
            model = None
    logging.info("Modelo cargado.")
    return model

def read_words(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            for word in line.split():
                yield word

def count_oov_words(model, words_txt_files, output_file):
    # Configurar el registro
    logging.basicConfig(filename=output_file, level=logging.INFO, format='%(asctime)s - %(message)s')

    # Obtener el vocabulario del modelo
    model_vocab = set(model.get_words()) if isinstance(model, fasttext.FastText._FastText) else set(model.vocab)

    # Contar las palabras fuera del vocabulario
    for txt_file in words_txt_files:
        start_time = time.time()
        oov_words = 0
        with open(txt_file, 'r') as f:
            for i, word in enumerate(read_words(txt_file)):
                if word not in model_vocab:
                    oov_words += 1
                if (i + 1) % 1000 == 0:
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    logging.info(f'Procesadas {i+1} palabras de {txt_file} en {elapsed_time} segundos')
        logging.info(f'Palabras OOV en {txt_file}: {oov_words}')

# Uso de las funciones
fichModel = '../datos/cc.en.300.bin'
words_txt_files = ['../datos/txt_reunidos_1_limpio.txt', '../datos/txt_reunidos_2_limpio.txt', '../datos/txt_reunidos_3_limpio.txt', '../datos/txt_reunidos_4_limpio.txt']
output_file = 'oov_log_fasttext.txt'

model = load_model(fichModel)
if model is not None:
    count_oov_words(model, words_txt_files, output_file)
