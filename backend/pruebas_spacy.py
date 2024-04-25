import spacy
import re

nlp = spacy.load('en_core_web_sm')

def obtain_english_words():

    words = set(nlp.vocab.strings)

    # Texto con la palabra compuesta por guión
    text = "According to a recent census from 140 countries worldwide [1], breast cancer is the most frequently diagnosed cancer in women, with an estimated incidence of 1.7 million new cases per year. It represents 25\% \of all types of cancers diagnosed in women furthermore, 15\% \of cancer death cite3457345 formulaw47534t37hfhh [ ] , weq 234234"


    text_lowercase = re.sub(r'[A-Z]', lambda match: match.group().lower(), text)

    # Procesar el texto con el modelo de spaCy
    doc = nlp(text_lowercase)

    # Obtener todas las palabras alfabéticas detectadas por spaCy
    obtained_words = [token.text for token in doc if token.is_alpha]

    # Filtrar palabras reales que estén en el diccionario de palabras en inglés y convertirlas a minúsculas
    real_words = [word for word in obtained_words if word in words]

    # Imprimir las palabras reales en minúsculas
    print(real_words)


def obtain_english_words2():

    # Texto con la palabra compuesta por guión
    text = "According to a recent census from 140 countries worldwide [1], breast cancer is the most frequently diagnosed cancer in women, with an estimated incidence of 1.7 million new cases per year. It represents 25\% \of all types of cancers diagnosed in women furthermore, 15\% \of cancer death cite3457345 formulaw47534t37hfhh [ ] , weq 234234"

    text_lowercase = re.sub(r'[A-Z]', lambda match: match.group().lower(), text)

    # Procesar el texto con el modelo de spaCy
    doc = nlp(text_lowercase)

    obtained_words = [token.text for token in doc if token.is_alpha]
    found_words = [word for word in obtained_words if nlp(word)[0].is_oov == False]
    print(found_words)


#obtain_english_words2()
obtain_english_words2()















