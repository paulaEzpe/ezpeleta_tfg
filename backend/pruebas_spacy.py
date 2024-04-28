import spacy
import re

############Probando spaCy#############

nlp = spacy.load('en_core_web_sm')

# Texto con la palabra compuesta por guión
text = "According to a recent census from 140 countries worldwide [1], breast cancer is the most frequently diagnosed cancer in women, with an estimated incidence of 1.7 million new cases per year. It represents 25\% \of all types of cancers diagnosed in women furthermore, 15\% \of cancer death cite3457345 formulaw47534t37hfhh [ ] , weq 234234"

cita = "According to a recent census from 140 countries worldwide, breast cancer is the most frequently diagnosed"

# dados dos strings, devuelve una lista con las palabras alfabéticas de cada uno de ellos
def obtain_list_english_words(texto, cita):

    # Poner en minúsculas el texto y la cita
    text_lowercase = re.sub(r'[A-Z]', lambda match: match.group().lower(), text)
    cite_lowercase = re.sub(r'[A-Z]', lambda match: match.group().lower(), cita)

    # Procesar el texto y la cita con el modelo de spaCy
    texto_procesado = nlp(text_lowercase)
    cita_procesada = nlp(cite_lowercase)

    # Obtener todas las palabras alfabéticas detectadas por spaCy
    obtained_text_words = [token.text for token in texto_procesado if token.is_alpha]
    obtained_cite_words = [token.text for token in cita_procesada if token.is_alpha]

    print("Lista de palabras del texto en inglés:")
    print(obtained_text_words)
    print("Lista de palabras de la cita en inglés:")
    print(obtained_cite_words)

    return obtained_text_words, obtained_cite_words

#############################################################################################################

# Funcion que dados dos conjuntos, devuelve true si el primero de ellos contiene al menos el 80% de las palabras del segundo
def contiene_suficientes_palabras(conjunto_parrafo, conjunto_cita):

    # Hacer un conteo de la cantidad de palabras de la cira que se encuentran en el parrafo
    palabras_encontradas = sum(1 for palabra in conjunto_cita if palabra in conjunto_parrafo)
    
    # Calcular el porcentaje 
    porcentaje_encontrado = (palabras_encontradas / len(conjunto_cita)) * 100
    
    if porcentaje_encontrado >= 80:
        return True
    else:
        return False

#############################################################################################################

def algoritmo(lista_parrafo, lista_cita):
    max_consecutivas = 0  # Inicializamos el máximo número de coincidencias consecutivas
    max_subsecuencia = []  # Inicializamos la subsecuencia más larga que coincide
    
    if contiene_suficientes_palabras(set(lista_parrafo), set(lista_cita)):
        # Iteramos sobre la lista de párrafo para considerar todas las subsecuencias posibles
        for i in range(len(lista_parrafo)):
            for j in range(i + 1, len(lista_parrafo) + 1):
                subsecuencia = lista_parrafo[i:j]
                
                # Iteramos sobre todas las subsecuencias posibles de la lista de cita
                for k in range(len(lista_cita)):
                    for l in range(k + 1, len(lista_cita) + 1):
                        subsecuencia_cita = lista_cita[k:l]
                        
                        # Si la subsecuencia del párrafo coincide con la subsecuencia de la cita, actualizamos max_consecutivas y max_subsecuencia
                        if subsecuencia == subsecuencia_cita:
                            if len(subsecuencia_cita) > max_consecutivas:
                                max_consecutivas = len(subsecuencia_cita)
                                max_subsecuencia = subsecuencia_cita
    else: 
        print("El párrafo no contiene suficientes palabras de la cita")
        # devolverá 0 y la lista vacía
    return max_consecutivas, max_subsecuencia
    
    
# Llamada a la función
lista_parrafo = ["hola", "que", "estas", "soy", "un", "párrafo", "con", "varias", "palabras", "que", "se", "repite", "tal", "estas", "soy", "un", "párrafo", "con", "varias", "palabras", "que", "se", "repite", "que", "estas", "soy", "un", "párrafo", "con", "varias", "palabras", "que", "se", "repite"]
lista_cita = ["que", "tal", "estas", "soy"]

resultado = algoritmo(lista_parrafo, lista_cita)
print("Máximo número de coincidencias consecutivas:", resultado)
    
















