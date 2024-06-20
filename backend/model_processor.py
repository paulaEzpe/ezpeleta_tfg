import os
import re
import requests
import numpy as np
import gensim
from numpy import dot
from numpy.linalg import norm
import fasttext
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util

import torch
from transformers import AutoTokenizer, AutoModel
from model import FNN, sentibert


class ModelProcessor:

    def __init__(self):
        self.modeloCargado = False
        # Lista de rutas a los archivos de modelo
        self.fichModels = [
            '../datos/cc.en.300.bin',
            '../datos/GoogleNews-vectors-negative300.bin',
            '../datos/modelo_reentrenado_2_4_18_19_20_21_22.model'
        ]
        self.models = []
        self.vocabularies = []

        self.model_path = "../datos/pesos_modelo.pt"  # Ajusta la ruta según donde hayas guardado el modelo
        self.base_model_path = "bert-base-uncased"  # Ruta al modelo base utilizado durante el entrenamiento

    # Función para cargar los modelos
    def cargarModelos(self):
        
        # Cargar modelos FastText
        fasttext_model = fasttext.load_model(self.fichModels[0])
        self.models.append(fasttext_model)
        self.vocabularies.append(set(fasttext_model.get_words()))

        # Cargar modelos KeyedVectors
        keyed_vectors_model = gensim.models.KeyedVectors.load_word2vec_format(self.fichModels[1], binary=True)
        self.models.append(keyed_vectors_model)
        self.vocabularies.append(list(keyed_vectors_model.key_to_index.keys()))

        # Cargar modelos Word2Vec
        word2vec_model = gensim.models.Word2Vec.load(self.fichModels[2])
        self.models.append(word2vec_model)
        self.vocabularies.append(list(word2vec_model.wv.key_to_index.keys()))



        # Cargar modelo BERT
        self.bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert_model = BertModel.from_pretrained("bert-base-uncased")
        self.bert_model.eval()

        # Cargar modelo SentenceTransformer
        self.sentence_model = SentenceTransformer('paraphrase-MiniLM-L12-v2')

        self.modeloCargado = True

    # Función para obtener la similitud entre una cita y un texto (se usa con el abstract, con todos los párrafos
    # para obtener el de mayor similitud...)
    def obtener_similitud_entre_cita_y_articulo(self, tokens_cita, tokens_articulo):
        if not self.modeloCargado:
            self.cargarModelos()
        similitudes = []

        # Para cada modelo
        for modelo, vocabulary in zip(self.models, self.vocabularies):
            vectores_cita = []
            numero_cita_desconocidas = 0
            numero_vector_desconocidas = 0
            numero_cita_conocidas = 0
            numero_vector_conocidas = 0

            # Obtener vectores de palabras para la cita
            for token in tokens_cita:
                try:
                    numero_cita_conocidas += 1
                    if isinstance(modelo, fasttext.FastText._FastText):
                        vector = modelo.get_word_vector(token)
                    elif isinstance(modelo, gensim.models.Word2Vec):
                        vector = modelo.wv[token]
                    else:
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
                    if isinstance(modelo, fasttext.FastText._FastText):
                        vector = modelo.get_word_vector(token)
                    elif isinstance(modelo, gensim.models.Word2Vec):
                        vector = modelo.wv[token]
                    else:
                        vector = modelo[token]
                    vectores_articulo.append(vector)
                except KeyError:
                    numero_vector_desconocidas += 1
                    # Manejar palabras desconocidas
                    pass

            # Promediar vectores de palabras para obtener representaciones vectoriales de la cita y el artículo
            representacion_cita = np.mean(vectores_cita, axis=0)
            representacion_articulo = np.mean(vectores_articulo, axis=0)

            # Comparar la similitud entre las representaciones vectoriales de la cita y el artículo, usando el coseno
            similitud = dot(representacion_cita, representacion_articulo) / (norm(representacion_cita) * norm(representacion_articulo))
            
            # Agregar la similitud a la lista de similitudes
            similitudes.append(similitud)

        # Calcular similitud usando BERT
        bert_similitud = self.obtener_similitud_bert(' '.join(tokens_cita), ' '.join(tokens_articulo))
        similitudes.append(bert_similitud)

        # Calcular similitud usando SentenceTransformer
        st_similitud = self.obtener_similitud_sentence_transformer(' '.join(tokens_cita), ' '.join(tokens_articulo))
        similitudes.append(st_similitud)

        return similitudes

    # Función para obtener la similitud entre dos frases usando BERT
    def obtener_similitud_bert(self, s1, s2):
        max_len = 512  # Longitud máxima permitida por BERT

        # Tokenizar las frases y dividirlas en fragmentos de longitud máxima
        tokens_s1 = self.bert_tokenizer.encode(s1, add_special_tokens=False, truncation=True, max_length=max_len-2)
        tokens_s2 = self.bert_tokenizer.encode(s2, add_special_tokens=False, truncation=True, max_length=max_len-2)

        def get_bert_embedding(tokens):
            embeddings = []
            for i in range(0, len(tokens), max_len - 2):  # Reservar espacio para [CLS] y [SEP]
                fragment = tokens[i:i + (max_len - 2)]
                fragment = self.bert_tokenizer.build_inputs_with_special_tokens(fragment)
                fragment_tensor = torch.tensor(fragment).unsqueeze(0)

                with torch.no_grad():
                    output = self.bert_model(fragment_tensor)

                embeddings.append(output.last_hidden_state.mean(dim=1).squeeze().numpy())

            return np.mean(embeddings, axis=0)

        embedding_s1 = get_bert_embedding(tokens_s1).reshape(1, -1)
        embedding_s2 = get_bert_embedding(tokens_s2).reshape(1, -1)

        cos_sim = cosine_similarity(embedding_s1, embedding_s2)[0][0]
        return cos_sim

    # Función para obtener la similitud entre dos frases usando SentenceTransformer
    def obtener_similitud_sentence_transformer(self, s1, s2):
        # Calcular las embeddings para ambas frases
        embedding_s1 = self.sentence_model.encode(s1, convert_to_tensor=True)
        embedding_s2 = self.sentence_model.encode(s2, convert_to_tensor=True)

        # Calcular la similitud coseno entre las embeddings
        cos_sim = util.pytorch_cos_sim(embedding_s1, embedding_s2).item()
        return cos_sim

    ################################POLARIDAD########################################

    def load_model(self, method_name="fnn"):
        # Cargar el tokenizador y el modelo base
        tokenizer = AutoTokenizer.from_pretrained(self.base_model_path, add_prefix_space=True)
        base_model = AutoModel.from_pretrained(self.base_model_path)

        # Inicializar el modelo específico
        if method_name == "fnn":
            model = FNN(base_model, 3)  # Asegúrate de definir num_classes
        elif method_name == "sentibert":
            model = sentibert(base_model, 3)  # Asegúrate de definir num_classes
        else:
            raise ValueError("Método desconocido")

        # Cargar pesos entrenados
        model_state_dict = torch.load(self.model_path, map_location=torch.device('cpu'))
        model.base_model.embeddings.word_embeddings.weight.data = model_state_dict['base_model.embeddings.word_embeddings.weight']
        model.load_state_dict(model_state_dict, strict=False)

        # Mover el modelo a la GPU si está disponible
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)

        # Poner el modelo en modo de evaluación
        model.eval()

        return model, tokenizer

    def predict_polarity(self, model, tokenizer, text, device):
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        input_ids = inputs["input_ids"].to(device)
        attention_mask = inputs["attention_mask"].to(device)
        return self.predict_polarity_from_inputs(model, {"input_ids": input_ids, "attention_mask": attention_mask})

    def predict_polarity_from_inputs(self, model, inputs):
        with torch.no_grad():
            probabilities = model(inputs)
        return probabilities.cpu().numpy()

    def calcular_polaridad(self, texto):
        model, tokenizer = self.load_model(method_name="fnn")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # probabilidades = self.predict_polarity(model, tokenizer, texto, device)
        probabilidades = self.predict_polarity(model, tokenizer, ' '.join(texto), device)
        print (f'texto: {" ".join(texto)} len: {texto}')
        print (f'len prob: {probabilidades}')
        return probabilidades[0]  # Devolver solo las probabilidades de la primera (y única) entrada

