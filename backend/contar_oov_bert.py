import logging
from transformers import BertTokenizer, BertModel
import torch
import time

# Configurar el registro
output_file = "oov_log_bert.log"
logging.basicConfig(filename=output_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_bert_model():
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased")
    model.eval()
    return tokenizer, model

def read_words(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            for word in line.split():
                yield word

def get_out_of_vocabulary_words_list(tokenizer, words):
    out_of_vocab_words = []
    for word in words:
        tokens = tokenizer.tokenize(word)
        out_of_vocab_words.extend([token for token in tokens if token not in tokenizer.vocab])
    return out_of_vocab_words

def count_oov_words(tokenizer, words_txt_files):
    for txt_file in words_txt_files:
        start_time = time.time()
        oov_words = 0
        total_words = 0
        for word in read_words(txt_file):
            total_words += 1
            tokens = tokenizer.tokenize(word)
            for token in tokens:
                if token not in tokenizer.vocab:
                    oov_words += 1
                    break  # No need to check further tokens if one is already OOV
            if total_words % 10000000 == 0:
                logging.info(f'Procesadas {total_words} palabras de {txt_file}')
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f'Palabras OOV en {txt_file}: {oov_words}')
        logging.info(f'Procesadas {total_words} palabras de {txt_file} en {elapsed_time:.2f} segundos')

# Uso de las funciones
words_txt_files = ['../datos/txt_reunidos_2_4_limpio.txt', '../datos/txt_reunidos_18_19_20_limpio.txt', '../datos/txt_reunidos_21_limpio.txt', '../datos/txt_reunidos_22_limpio.txt']

tokenizer, model = load_bert_model()
count_oov_words(tokenizer, words_txt_files)
