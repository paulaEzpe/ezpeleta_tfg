"""-------------------------------------------------------------------------
Nombre del archivo: compare_sentences.py
Autora:             Paula Ezpeleta Castrillo
Fecha de creación:  15/05/2024
Descripción:        Módulo correspondiente a todas las operaciones a realizar con texto
-------------------------------------------------------------------------"""

import re
import spacy
import time

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

    # Funcion para extraer las citas de un texto (generalmente del parrafo de la seleccion)
    @staticmethod
    def extraer_citas(texto):
        # Expresión regular para encontrar citas
        patron = r'\{\{cite:[^\}]+\}\}'
        # Encontrar todas las coincidencias de la expresión regular en el texto
        citas_encontradas = re.findall(patron, texto)
        # Devolver las citas encontradas
        return citas_encontradas


    # Dados dos strings, devuelve dos lista con las palabras alfabéticas de cada uno de ellos
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

    # Funcion para obtener una lista de palabras alfabéticas a partir de un texto
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
    # Esta función se utiliza para comprobar si un parrafo contiene suficientes palabras de una cita, para poder
    # decir que esa cita corresponde a ese parrafo
    def contiene_suficientes_palabras(conjunto_parrafo, conjunto_cita):

        # Hacer un conteo de la cantidad de palabras de la cira que se encuentran en el parrafo
        palabras_encontradas = sum(1 for palabra in conjunto_cita if palabra in conjunto_parrafo)
        
        # Calcular el porcentaje 
        porcentaje_encontrado = (palabras_encontradas / len(conjunto_cita)) * 100
        
        if porcentaje_encontrado >= 80:
            return True
        else:
            return False

    
    @staticmethod
    # Función para extraer el texto entre dos patrones usando una expresión regular
    def extraer_texto_desde_patrones_old(texto):
    # Expresión regular para buscar desde 'ABSTRACT' hasta 'INTRODUCTION'
        patron_abstract_intro = re.search(r'((A|a)(B|b)(S|s)(T|t)(R|r)(A|a)(C|c)(T|t))((.|\n)+?)(?=(I|i)(N|n)(T|t)(R|r)(O|o)(D|d)(U|u)(C|c)(T|t)(I|i)(O|o)(N|n))', texto, re.DOTALL)
        
        # Inicializar los textos extraídos
        texto_abstract_intro = None
        texto_intro_en_adelante = None

        if patron_abstract_intro:
            # Texto desde 'ABSTRACT' hasta justo antes de 'INTRODUCTION'
            texto_abstract_intro = patron_abstract_intro.group(8)
            
            # Buscar el inicio del texto 'INTRODUCTION' en adelante
            patron_intro_en_adelante = re.search(r'(I|i)(N|n)(T|t)(R|r)(O|o)(D|d)(U|u)(C|c)(T|t)(I|i)(O|o)(N|n)', texto)
            if patron_intro_en_adelante:
                inicio_intro = patron_intro_en_adelante.start()
                texto_intro_en_adelante = texto[inicio_intro:]
        
        return texto_abstract_intro, texto_intro_en_adelante

    def extraer_texto_desde_patrones(texto):
        r1 = '((.|\n)+)'
        r2 = '[Aa][Bb][Ss][Tt][Rr][Aa][Cc][Tt]'
        r3 = '((.|\n)+?)'
        r4 = '[Ii][Nn][Tt][Rr][Oo][Dd][Uu][Cc][Tt][Ii][Oo][Nn]'
        r5 = '((.|\n)+)'
        result = re.match(r1 + r2 + r3 + r4 + r5, texto)
        if result:
            # parece que pre_abstract y abstract están en los grupos 1 y 3, respectivamente
            pre_abstract = result.group(1).replace('\n', ' ').replace('\t', ' ')
            abstract = result.group(3).replace('\n', ' ').replace('\t', ' ')
            cuerpo = result.group(5)
            # Reemplaza '.\n' por '.\n\n' para separar en párrafos
            cuerpo = re.sub(r'\.\n', '.\n\n', cuerpo)
        return abstract, cuerpo


#---------------------------------------------------

    ######################3ALGORITMO NAIVE########################

    # Dadas dos listas de strings, da la longitud del mayor
    # prefijo comun, empezando en los índices i1, i2, respectivamente
    @staticmethod
    def longestPrefixIndex(list_1,i1,list_2,i2, maxLongPosible):
        k = 0
        while k < maxLongPosible and list_1[i1+k] == list_2[i2+k]:
            k += 1
    
        return k
 

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

    # Para entender qué hacen las funciones, leer especificación del algoritmo

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
