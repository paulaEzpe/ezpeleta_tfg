# """-------------------------------------------------------------------------
# Nombre del archivo: compare_sentences_2.py
# Autora:             Paula Ezpeleta Castrillo
# Fecha de creación:  15/05/2024
# Descripción:        Codigo necesario para la comparación de similitud entre textos usando sentence-transformers y BERT
# -------------------------------------------------------------------------"""



# # https://stackoverflow.com/questions/60492839/how-to-compare-sentence-similarities-using-embeddings-from-bert
# # Usando sentence-transformers y BERT (están optimizados específicamente para tareas de similitud de oraciones y pueden proporcionar mejores resultados en comparación con el uso directo de BERT sin ajustes adicionales)
# import sys
# from sentence_transformers import SentenceTransformer, util
# model = SentenceTransformer('paraphrase-MiniLM-L12-v2')

# # Two lists of sentences

# s1 = ['The cat sits outside',
#              'A man is playing guitar',
#              'The new movie is awesome']

# s2 = ['The dog plays in the garden',
#               'A woman watches TV',
#               'The new movie is so great']

# s1 = ['In this chapter we introduce mechanisms for declaring new types and classes in Haskell. We start with three approaches to declaring types, then consider recursive types, show how to declare classes and their instances, and conclude by developing a tautology checker and an abstract machine']

# s2 = [
#     'In this chapter, we explore methods for defining new types and classes in Haskell. We begin with three techniques for declaring types, followed by a discussion on recursive types. Next, we demonstrate how to declare classes and their instances. Finally, we conclude by creating a tautology checker and an abstract machine',
#     'He says they are showing how to declare classes and instances',
#     'They do not show how to declare classes and instances',
#     'In this chapter we present mechanisms for declaring new classes',
#     'It seems the authors propose the use of Haskell',
#     'It seems the authors are against the use of Haskell',
#     'This is bullshit'
# ]
# #----------------------------------------------------------
# def get():
#     sys.stdout.write('--> ')
#     return input()
# #----------------------------------------------------------
# def show_results(scores):
#     for i in range(len(scores)):
#         s = scores[i]
#         print("(%d,%d): %f"%(s[0][0],s[0][1],s[1]))
# #---------------------------------------------------------

# #Compute embedding for both lists
# embeddings1 = model.encode(s1, convert_to_tensor=True)
# embeddings2 = model.encode(s2, convert_to_tensor=True)

# #Compute cosine-similarits
# cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)

# scores = dict()
# #Output the pairs with their score
# for i in range(len(s1)):
#     for j in range(len(s2)):
#         # print("{} \t\t {} \t\t Score: {:.4f}".format(s1[i], s2[i], cosine_scores[i][i]))
#         # print("--------------------------------")
#         # print("(%d,%d): %f"%(i,j,cosine_scores[i][j]))
#         scores[(i,j)] = cosine_scores[i][j].item()

# sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
# show_results(sorted_scores)

# print()
# newSentence = get()
# while newSentence != '':
#     embeddings2 = model.encode([newSentence], convert_to_tensor=True)
#     cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)
#     print("--------------------------------")
#     print("%f: '%s'"%(cosine_scores[0][0],newSentence))
#     newSentence = get()


# Usando sentence-transformers y BERT (están optimizados específicamente para tareas de similitud de oraciones y pueden proporcionar mejores resultados en comparación con el uso directo de BERT sin ajustes adicionales)
# https://stackoverflow.com/questions/60492839/how-to-compare-sentence-similarities-using-embeddings-from-bert
# Usando sentence-transformers y BERT (están optimizados específicamente para tareas de similitud de oraciones y pueden proporcionar mejores resultados en comparación con el uso directo de BERT sin ajustes adicionales)
# https://stackoverflow.com/questions/60492839/how-to-compare-sentence-similarities-using-embeddings-from-bert
# Usando sentence-transformers y BERT (están optimizados específicamente para tareas de similitud de oraciones y pueden proporcionar mejores resultados en comparación con el uso directo de BERT sin ajustes adicionales)
# https://stackoverflow.com/questions/60492839/how-to-compare-sentence-similarities-using-embeddings-from-bert
# Usando sentence-transformers y BERT (están optimizados específicamente para tareas de similitud de oraciones y pueden proporcionar mejores resultados en comparación con el uso directo de BERT sin ajustes adicionales)
import sys
from transformers import BertTokenizer
from nltk.tokenize import word_tokenize

# Inicializar el tokenizador BERT
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def identify_oov_words(sentence):
    # Tokenizar la oración a nivel de palabra
    words = word_tokenize(sentence)
    
    # Verificar si cada palabra está en el vocabulario de BERT
    oov_words = [word for word in words if word.lower() not in tokenizer.vocab]
    
    return oov_words

# Ejemplo de uso
sentence = "In this chapter we introduce mechanisms for declaring new types and classes in Haskell. We start with three approaches to declaring types, then consider recursive types, show how to declare classes and their instances, and conclude by developing a tautology checker and an abstract machine daedheudh hhdhhhhhhd hola"
oov_words = identify_oov_words(sentence)
print("Palabras OOV:", oov_words)
