from gensim.models import KeyedVectors
import fasttext
import time
from gensim.models import Word2Vec

def load_model(fichModel):
    try:
        # Intenta cargar el modelo con fasttext
        model = fasttext.load_model(fichModel)
    except Exception as e:
        print(f"Error al cargar el modelo con load: {e}")
        try:
            # Si falla, intenta cargar el modelo con KeyedVectors
            model = KeyedVectors.load_word2vec_format(fichModel, binary=True)
        except Exception as e:
            print(f"Error al cargar el modelo con KeyedVectors: {e}")
            model = None
    print("Modelo cargado.")
    return model

def count_oov_words(model, words_txt_file, output_file):
    # Leer las palabras del archivo .txt
    with open(words_txt_file, 'r') as f:
        words = f.read().split()

    # Obtener el vocabulario del modelo
    model_vocab = set(model.get_words()) if isinstance(model, fasttext.FastText._FastText) else set(model.vocab)

    # Contar las palabras fuera del vocabulario
    oov_words = []
    start_time = time.time()
    for i, word in enumerate(words):
        if word not in model_vocab:
            oov_words.append(word)
        if (i + 1) % 1000 == 0:
            print(f'Procesadas {i + 1} palabras.')
    num_oov_words = len(oov_words)
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Redirigir la salida a un archivo
    with open(output_file, 'a') as f:
        print(f'Modelo usado: {model}', file=f)
        print(f'Txt usado: {words_txt_file}', file=f)
        print(f'Número de palabras fuera del vocabulario: {num_oov_words}', file=f)
        print('Palabras fuera del vocabulario:', ' '.join(oov_words), file=f)
        print(f'Tiempo transcurrido: {elapsed_time} segundos', file=f)
        print('', file=f)  # Imprime un salto de línea

# Uso de las funciones
fichModel = '../datos/cc.en.300.bin'
words_txt_file = '../datos/txt_reunidos_21_limpio.txt'
output_file = 'oov_.txt'

model = load_model(fichModel)
if model is not None:
    count_oov_words(model, words_txt_file, output_file)