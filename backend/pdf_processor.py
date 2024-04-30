import PyPDF2
import os
import re
import requests

class PDFProcessor:
    def __init__(self):
        pass

    # Para extraer el paper_id del pdf de archive que busquemos
    def extraer_arxiv(texto):
        regex = r"arXiv:(\d+\.\d+(?:v\d+)?)"
        match = re.search(regex, texto)
        if match:
            resultado = match.group(1)  # Obtiene el texto coincidente
            resultado_sin_v = resultado.split('v')[0]  # Elimina 'v' y lo que le sigue
            return resultado_sin_v
        else:
            return None 
    
    def extraer_arxiv_de_entry_raw(referencia):
        regex = r"arXiv:(\d+\.\d+)"  # \D coincide con cualquier carácter que no sea un número
        match = re.search(regex, referencia)
        if match:
            id_arxiv_referencia = match.group(1)  # Obtiene el texto coincidente
            return id_arxiv_referencia
        else:
            return None

    # Para descargarme el pdf correspondiente cuando solo me pasan el id del paper por el input
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
            return ruta_pdf  # Devuelve la ruta del PDF descargado
        else:
            print(f"No se pudo descargar el PDF. Código de estado: {response.status_code}")
            return None  # Devuelve None si no se pudo descargar el PDF

    
    # Función auxiliar para extraer el texto de un pdf
    def extraer_texto_pdf(ruta_pdf):
        texto = ""
        with open(ruta_pdf, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                texto += page.extract_text()
        return texto
    # Ejemplo de uso
    # texto_extraido, ruta_del_pdf = descargar_y_extraer_texto_pdf_arxiv("1401.4766", "../datos/")
    # print("Texto extraído del PDF:")
    # print(texto_extraido)
    
    
    # Función para descargar un pdf y extraer su texto
    def descargar_y_extraer_texto_pdf_arxiv(arxiv_id, directorio_destino):
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
            texto = PDFProcessor.extraer_texto_pdf(ruta_pdf)
            return texto, ruta_pdf  # Devuelve el texto extraído y la ruta del PDF descargado
        else:
            print(f"No se pudo descargar el PDF. Código de estado: {response.status_code}")
            return None, None  # Devuelve None si no se pudo descargar el PDF

    
