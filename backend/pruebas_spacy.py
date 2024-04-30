import spacy
import re
import time

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
        # Creamos un diccionario para almacenar el índice de cada palabra en lista_cita
        indices_cita = {palabra: i for i, palabra in enumerate(lista_cita)}

        # Iteramos sobre la lista de párrafo para considerar todas las subsecuencias posibles
        for i in range(len(lista_parrafo)):
            for j in range(i + 1, len(lista_parrafo) + 1):
                subsecuencia = lista_parrafo[i:j]

                # Verificamos si las palabras en subsecuencia aparecen en lista_cita en el mismo orden
                k = -1
                for palabra in subsecuencia:
                    if palabra in indices_cita and indices_cita[palabra] > k:
                        k = indices_cita[palabra]
                    else:
                        break
                else:
                    # Si la subsecuencia del párrafo coincide con la subsecuencia de la cita, actualizamos max_consecutivas y max_subsecuencia
                    if j - i > max_consecutivas:
                        max_consecutivas = j - i
                        max_subsecuencia = subsecuencia

    else:
        print("El párrafo no contiene suficientes palabras de la cita")
        # devolverá 0 y la lista vacía
    return max_consecutivas, max_subsecuencia
    

###########################################################################


# dadas dos listas de strings, da la longitud del mayor
# prefijo comun, empezando en los índices i1, i2, respectivamente
def longestPrefixIndex(list_1,i1,list_2,i2):
    minLen = min((len(list_1)-i1,len(list_2)-i2))
    k = 0
    while k < minLen and list_1[i1+k] == list_2[i2+k]:
        k += 1
 
    return k
#---------------------------------------------------   
# dos listas de palabras

def longestCommonSubseq(list_1, list_2):
    longest = 0
    if contiene_suficientes_palabras(set(list_1), set(list_2)):
        #obtener el prefijo común más largo empezando en i1 e i2
        for i1 in range(len(list_1)):
            for i2 in range(len(list_2)):
                longestPartial = longestPrefixIndex(list_1,i1,list_2,i2)
                if longestPartial > longest:
                    longest = longestPartial


    return longest

#---------------------------------------------------

    
# Llamada a la función
lista_parrafo = ["hola", "que", "estas", "soy", "un", "párrafo", "con", "varias", "palabras", "que", "se", "repite", "tal", "estas", "soy", "un", "párrafo", "con", "varias", "palabras", "que", "se", "repite", "que", "estas", "soy", "un", "párrafo", "con", "varias", "palabras", "que", "se", "repite"]
lista_cita = ["que", "tal", "estas", "soy"]

start_time = time.perf_counter()
long = longestCommonSubseq(lista_parrafo, lista_cita)
end_time = time.perf_counter()
tiempo_de_ejecucion = end_time - start_time
print("El tiempo de ejecución de longestCommonSubseq es:", tiempo_de_ejecucion, "segundos.")
print('l1: %s\nl2: %s'%(lista_parrafo,lista_cita))
print('longest: %d'%(long))

start_time = time.perf_counter()
resultado = algoritmo(lista_parrafo, lista_cita)
end_time = time.perf_counter()
tiempo_de_ejecucion = end_time - start_time
print("El tiempo de ejecución de algoritmo es:", tiempo_de_ejecucion, "segundos.")
print("Máximo número de coincidencias consecutivas:", resultado)
    
















