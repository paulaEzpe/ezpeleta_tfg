import re
import spacy
import time

############Probando spaCy#############

nlp = spacy.load('en_core_web_sm')

class TextProcessor:


    def __init__(self):
        pass


    @staticmethod
    def limpiar_texto(texto):
        # Eliminar secuencias de números y letras seguidos
        texto_limpio = re.sub(r'\b\w+\d+\w*\b', '', texto.lower())
        # Eliminar caracteres no alfanuméricos y convertir a minúsculas
        texto_limpio = re.sub(r'[^\w\s]', '', texto_limpio)
        # Dividir el texto en palabras
        palabras = texto_limpio.split()
        return palabras

    @staticmethod
    def extraer_citas(texto):
        # Expresión regular para encontrar citas
        patron = r'\{\{cite:[^\}]+\}\}'
        # Encontrar todas las coincidencias de la expresión regular en el texto
        citas_encontradas = re.findall(patron, texto)
        # Retornar las citas encontradas
        return citas_encontradas


    # dados dos strings, devuelve una lista con las palabras alfabéticas de cada uno de ellos
    @staticmethod
    def obtain_list_english_words(texto, cita):

        # Poner en minúsculas el texto y la cita
        text_lowercase = re.sub(r'[A-Z]', lambda match: match.group().lower(), texto)
        cite_lowercase = re.sub(r'[A-Z]', lambda match: match.group().lower(), cita)

        # Procesar el texto y la cita con el modelo de spaCy
        texto_procesado = nlp(text_lowercase)
        cita_procesada = nlp(cite_lowercase)

        # Obtener todas las palabras alfabéticas detectadas por spaCy
        obtained_text_words = [token.text for token in texto_procesado if token.is_alpha]
        obtained_cite_words = [token.text for token in cita_procesada if token.is_alpha]

        return obtained_text_words, obtained_cite_words

    @staticmethod
    def obtain_list_english_words_from_body(texto):
        # Poner en minúsculas el texto y la cita
        text_lowercase = texto

        # Procesar el texto y la cita con el modelo de spaCy
        texto_procesado = nlp(text_lowercase)

        # Obtener todas las palabras alfabéticas detectadas por spaCy
        obtained_text_words = [token.text for token in texto_procesado if token.is_alpha]

        return obtained_text_words


    @staticmethod
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

#---------------------------------------------------

    # dadas dos listas de strings, da la longitud del mayor
    # prefijo comun, empezando en los índices i1, i2, respectivamente
    @staticmethod
    def longestPrefixIndex(list_1,i1,list_2,i2, maxLongPosible):
        k = 0
        while k < maxLongPosible and list_1[i1+k] == list_2[i2+k]:
            k += 1
    
        return k
 
    # guardar el set de la cita fuera del bucle
    def longestCommonSubseq(self, list_1, list_2):
        longest = 0
        if self.contiene_suficientes_palabras(set(list_1), set(list_2)):
            #obtener el prefijo común más largo empezando en i1 e i2
            for i1 in range(len(list_1)):
                for i2 in range(len(list_2)):
                    maxLongPosible = min((len(list_1)-i1,len(list_2)-i2))
                    longestPartial = self.longestPrefixIndex(list_1,i1,list_2,i2,maxLongPosible)
                    if longestPartial == maxLongPosible:
                        return longestPartial
                    if longestPartial > longest:
                        longest = longestPartial

        return longest

    #########################Algoritmo KMP###########################

    @staticmethod
    def compute_prefix_function(pattern):
        m = len(pattern)
        pi = [0] * m
        k = 0
        for q in range(1, m):
            while k > 0 and pattern[k] != pattern[q]:
                k = pi[k - 1]
            if pattern[k] == pattern[q]:
                k += 1
            pi[q] = k
        return pi

    @staticmethod
    def kmp_search(text, pattern):
        n = len(text)
        m = len(pattern)
        pi = TextProcessor.compute_prefix_function(pattern)
        q = 0
        maxLong = 0 
        for i in range(n):
            while q > 0 and pattern[q] != text[i]:
                q = pi[q - 1]
            if pattern[q] == text[i]:
                q += 1
                maxLong = max(maxLong, q)
            else:
                q = 0
        return maxLong

    def longestCommonSubseq_KMP(self, pattern, text):
        maxLong = 0
        if self.contiene_suficientes_palabras(set(pattern), set(text)):
            for i in range(len(pattern)):
                partialLong = self.kmp_search(text, pattern[i:])
                maxLong = max(maxLong, partialLong)
        return maxLong
