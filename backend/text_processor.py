import re

class TextProcessor:
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
