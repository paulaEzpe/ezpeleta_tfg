import logging
from gensim.models import KeyedVectors
import fasttext
import time

# Configurar el registro
output_file = "oov_log_fasttext.log"
logging.basicConfig(filename=output_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_model(fichModel):
    try:
        # Intenta cargar el modelo con fasttext
        model = fasttext.load_model(fichModel)
        logging.info("Modelo cargado exitosamente con fasttext.")
    except Exception as e:
        logging.error(f"Error al cargar el modelo con fasttext: {e}")
        try:
            # Si falla, intenta cargar el modelo con KeyedVectors
            model = KeyedVectors.load_word2vec_format(fichModel, binary=True)
            logging.info("Modelo cargado exitosamente con KeyedVectors.")
        except Exception as e:
            logging.error(f"Error al cargar el modelo con KeyedVectors: {e}")
            model = None
    return model

def read_words(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            for word in line.split():
                yield word

def count_oov_words(model, words_txt_files):
    # Obtener el vocabulario del modelo como un conjunto para búsquedas rápidas
    model_vocab = set(model.get_words())

    # Contar las palabras fuera del vocabulario
    for txt_file in words_txt_files:
        start_time = time.time()
        oov_words = 0
        total_words = 0
        for word in read_words(txt_file):
            total_words += 1
            if word not in model_vocab:
                oov_words += 1
            if total_words % 10000000 == 0:
                logging.info(f'Procesadas {total_words} palabras de {txt_file}')
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f'Palabras OOV en {txt_file}: {oov_words}')
        logging.info(f'Procesadas {total_words} palabras de {txt_file} en {elapsed_time:.2f} segundos')

# Uso de las funciones
fichModel = '../datos/cc.en.300.bin'
words_txt_files = ['../datos/txt_reunidos_2_4_limpio.txt', '../datos/txt_reunidos_18_19_20_limpio.txt', '../datos/txt_reunidos_21_limpio.txt', '../datos/txt_reunidos_22_limpio.txt']

model = load_model(fichModel)
if model is not None:
    count_oov_words(model, words_txt_files)
