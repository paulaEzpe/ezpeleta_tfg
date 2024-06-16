import gensim

model_path = "../datos/modelo_reentrenado_2_4_18_19_20_21_22.model"
try:
    word2vec_model = gensim.models.Word2Vec.load(model_path)
    vocabulary = list(word2vec_model.wv.key_to_index.keys())
    print("Modelo .model cargado correctamente")
except Exception as e:
    print(f"Error al cargar el modelo .model: {e}")