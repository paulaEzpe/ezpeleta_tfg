# import spacy
# import re
# from fuzzywuzzy import fuzz
# from autocorrect import Speller

# ############Probando spaCy#############

# nlp = spacy.load('en_core_web_sm')

# def obtain_english_words():

#     words = set(nlp.vocab.strings)

#     # Texto con la palabra compuesta por guión
#     text = "According to a recent census from 140 countries worldwide [1], breast cancer is the most frequently diagnosed cancer in women, with an estimated incidence of 1.7 million new cases per year. It represents 25\% \of all types of cancers diagnosed in women furthermore, 15\% \of cancer death cite3457345 formulaw47534t37hfhh [ ] , weq 234234"

#     text_lowercase = re.sub(r'[A-Z]', lambda match: match.group().lower(), text)

#     # Procesar el texto con el modelo de spaCy
#     doc = nlp(text_lowercase)

#     # Obtener todas las palabras alfabéticas detectadas por spaCy
#     obtained_words = [token.text for token in doc if token.is_alpha]

#     # Filtrar palabras reales que estén en el diccionario de palabras en inglés y convertirlas a minúsculas
#     real_words = [word for word in obtained_words if word in words]

#     print(real_words)
#     return real_words


# # def obtain_english_words2():

# #     # Texto con la palabra compuesta por guión
# #     text = "According to a recent census from 140 countries worldwide [1], breast cancer is the most frequently diagnosed cancer in women, with an estimated incidence of 1.7 million new cases per year. It represents 25\% \of all types of cancers diagnosed in women furthermore, 15\% \of cancer death cite3457345 formulaw47534t37hfhh [ ] , weq 234234"

# #     text_lowercase = re.sub(r'[A-Z]', lambda match: match.group().lower(), text)

# #     # Procesar el texto con el modelo de spaCy
# #     doc = nlp(text_lowercase)

# #     obtained_words = [token.text for token in doc if token.is_alpha]
# #     found_words = [word for word in obtained_words if nlp(word)[0].is_oov == False]
# #     print(found_words)



# #obtain_english_words2()

# ############Probando fuzzywuzzy#############

# # Ejemplo de lista de palabras de la cita y cadena de texto del párrafo
# from fuzzywuzzy import fuzz

# palabras_parrafo = ['according', 'to', 'a', 'recent', 'census', 'from', 'countries', 'worldwide', 'breast', 'cancer', 'is', 'the', 'most', 'frequently', 'diagnosed', 'cancer', 'in', 'women', 'with', 'an', 'estimated', 'incidence', 'of', 'million', 'new', 'cases', 'per', 'year', 'it', 'represents', 'all', 'types', 'of', 'cancers', 'diagnosed', 'in', 'women', 'furthermore', 'cancer', 'death']
# palabras_cita = ['cording', 'to', 'a', 'recent', 'census', 'from', 'countries', 'worldwide', 'breast', 'cancer', 'is', 'the', 'most', 'frequently', 'diagnosed', 'cancer', 'in', 'women', 'with', 'an', 'estimated', 'incidence', 'of', 'million', 'new', 'cases', 'per', 'year', 'it', 'represents', 'all', 'types', 'of', 'cancers', 'diagnosed', 'in', 'women', 'furthermore', 'cancer', 'dea']

# def obtener_similitud(palabras_cita, palabras_parrafo):

#     # Umbral de similitud para la primera y última palabra de la cita
#     umbral_similitud_primera_ultima = 70

#     # Verificar si hay alguna coincidencia entre las palabras de la cita y las del párrafo
#     coincidencias_primera_ultima = (fuzz.ratio(palabras_cita[0], palabras_parrafo[0]) >= umbral_similitud_primera_ultima and
#                                     fuzz.ratio(palabras_cita[-1], palabras_parrafo[-1]) >= umbral_similitud_primera_ultima)

#     # Verificar coincidencia del 100% para las palabras entre la primera y la última
#     coincidencias_intermedias = (palabras_cita[1:-1] == palabras_parrafo[1:-1])

#     if coincidencias_primera_ultima and coincidencias_intermedias:
#         print("Las listas coinciden")
#     else:
#         print("Las listas no coinciden")


# ##########Probando el autocorrect#############

# # # Lista de palabras incompletas
# # lista_incompleta = ["naranj", "sill"]

# # # Corregir las palabras incompletas en la lista
# # corrector = Speller()
# # lista_corregida = [corrector(palabra) for palabra in lista_incompleta]

# # # Imprimir la lista corregida
# # print("Lista corregida:")
# # print(lista_corregida)

# #obtain_english_words()
# obtener_similitud(palabras_cita, palabras_parrafo)







import os
import requests
import PyPDF2



def descargar_pdf_arxiv(arxiv_id, directorio_destino):
    # Construye la URL del PDF
    url_pdf = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    # Descarga el PDF
    response = requests.get(url_pdf)
    if response.status_code == 200:
        
        # Guarda el PDF en el directorio especificado
        ruta_pdf = os.path.join(directorio_destino, f"{arxiv_id}.pdf")
        with open(ruta_pdf, 'wb') as f:
            f.write(response.content)
        print(f"PDF descargado correctamente: {ruta_pdf}")
        
        # Extraer texto del PDF
        texto = extraer_texto_pdf(ruta_pdf)
        return texto, ruta_pdf  # Devuelve el texto extraído y la ruta del PDF descargado
    else:
        print(f"No se pudo descargar el PDF. Código de estado: {response.status_code}")
        return None, None  # Devuelve None si no se pudo descargar el PDF

def extraer_texto_pdf(ruta_pdf):
    texto = ""
    with open(ruta_pdf, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page in pdf_reader.pages:
            texto += page.extract_text()
    return texto
# Ejemplo de uso
texto_extraido, ruta_del_pdf = descargar_pdf_arxiv("1401.4766", "../datos/")
print("Texto extraído del PDF:")
print(texto_extraido)










