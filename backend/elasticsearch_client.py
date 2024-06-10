"""-------------------------------------------------------------------------
Nombre del archivo: compare_sentences.py
Autora:             Paula Ezpeleta Castrillo
Fecha de creación:  15/05/2024
Descripción:        Módulo correspondiente a todas las operaciones a realizar con OpenSearch
-------------------------------------------------------------------------"""

from opensearchpy import OpenSearch
from pdf_processor import PDFProcessor
from text_processor import TextProcessor
import json
import time

class ElasticsearchClient:
    def __init__(self, host='localhost', port=9200, auth=('admin', 'admin'), ca_certs_path='/full/path/to/root-ca.pem'):
        self.host = host
        self.port = port
        self.auth = auth
        self.ca_certs_path = ca_certs_path
        self.client = self._connect()
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()

    def _connect(self):
        # Create the client with SSL/TLS enabled, but hostname verification disabled.
        client = OpenSearch(
            hosts=[{'host': self.host, 'port': self.port}],
            http_compress=True, 
            http_auth=self.auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            ca_certs=self.ca_certs_path
        )
        return client

    
    def verify_connection(self):
        try:
            info_cluster = self.client.info()
            if info_cluster:
                print("¡Conexión establecida correctamente!")
                print("Información del clúster:", info_cluster)
                return True
            else:
                print("No se pudo obtener la información del clúster.")
                return False
        except Exception as e:
            print("Error al intentar obtener información del clúster:", e)
            return False
        
    def obtener_titulo_por_paper_id(self, index_name, paper_id):
        # Realiza una búsqueda utilizando el paper_id como filtro
        resultado = self.client.search(index=index_name, body={"query": {"term": {"paper_id": paper_id}}}, _source=["title"])
        hits = resultado["hits"]["hits"]
        # Verifica si hay resultados
        if hits:
            for hit in hits:
                return hit["_source"]["title"]  # Devuelve el título del documento encontrado
        else:
            return None  # Devuelve None si no se encontró ningún documento con el paper_id dado

    def obtener_json_por_paper_id_u_obtener_texto(self, index_name, paper_id_referencia):
        resultado = self.client.search(
            index=index_name,
            body={
                "query": {
                    "match": {
                        "paper_id": paper_id_referencia
                    }
                }
            }
        )
        print("El id del docukento que se esta buscando es:", paper_id_referencia)
        hits = resultado["hits"]["hits"]
        if hits: 
            documento_especifico = hits[0]["_source"]
            # Acceder al campo json_data para obtener el documento serializado
            documento_serializado = documento_especifico["json_data"]

            # Deserializar el documento serializado para obtener el documento original
            documento_original = json.loads(documento_serializado)

            # Acceder al campo body_text del documento original
            body_text = documento_original["body_text"]

            abstract_obj = documento_original.get("abstract", {})
            abstract_texto = abstract_obj.get("text", "") + "\n"

            texto_cuerpo_json = ""

            for obj in body_text:
                # cojo el parrafo
                texto = obj["text"]
                texto_parrafo_limpio = self.text_processor.limpiar_texto(texto)
                texto_parrafo = ' '.join(texto_parrafo_limpio)
                texto_cuerpo_json += texto_parrafo + "\n" + "\n"

            texto_cuerpo_json = texto_cuerpo_json + "\n"

            return texto_cuerpo_json, abstract_texto
        else:
            print("como no se ha encontrado el documento en la base de datos, lo descargo y extraigo el texto")
            # Si el paper_id no se encuentra en la base de datos, descargar y extraer el PDF
            texto_pdf, _ = PDFProcessor.descargar_y_extraer_texto_pdf_arxiv(paper_id_referencia, "../datos/")
            processor = TextProcessor()
            texto_abstract, texto_cuerpo = TextProcessor.extraer_texto_desde_patrones(texto_pdf)
            #aqui habria que meter lo de la expresion regular para obtener el abstract
            abstract_descargado = texto_abstract + "\n"
            cuerpo_descargado = texto_cuerpo + "\n"
            return cuerpo_descargado, abstract_descargado

    # Implementado con mi algoritmo
    def obtener_bibliografia_texto_parrafo_seleccion(self, index_name, paper_id, cita):
        consulta = {"query": {"match": {"paper_id": paper_id}}}   
        # Realizar la consulta para obtener el documento específico
        resultado = self.client.search(index=index_name, body=consulta)
        # Obtener el documento específico de los resultados
        documento_especifico = resultado["hits"]["hits"][0]["_source"]

        # Acceder al campo json_data para obtener el documento serializado
        documento_serializado = documento_especifico["json_data"]

        # Deserializar el documento serializado para obtener el documento original
        documento_original = json.loads(documento_serializado)

        # Acceder al campo body_text del documento original
        body_text = documento_original["body_text"]
        # cojo las referencias de las citas del documento original
        bibliografia = documento_original["bib_entries"]

        #para almacenar el parrafo en el que se encuentra la cita
        parrafo_cita = ""

        bibliografia_completa = ""  # Inicializar el string de la bibliografía

        mejor_parrafo = ""
        max_coincidencias = 0
        mejor_citas = []

        processor = TextProcessor()
        texto_cita_limpio = processor.limpiar_texto(cita)
        texto_cita_limpio_string = ' '.join(texto_cita_limpio)
        for obj in body_text:
            # cojo el parrafo
            texto = obj["text"]
            # cojo las citas del parrafo
            citas = obj["cite_spans"]
            # print("Las citas de cada parrafo son: ", citas)
            # esto habrá que sustiruirlo por el algoritmo nuevo implementado, convirtiendoi primero texto_cita_limpio y 
            # texto_parrafo_limpio en listas, con la funcion obtain_list_english_words, y luego comparando si está en el párrafo con el algoritmo

            # Tengo que moidificar esto para que en vez de coger texto tal cual de la cita, primero lo tokenice, y lo compare con los párrafos, necesitando un 90% de coincnidencia entre las palabras, por si la selección de la cita, se come algo del principio o del final de una palabra
            texto_parrafo_limpio = processor.limpiar_texto(texto)
            # print("ha llamado a text_processor bien")
            texto_parrafo = ' '.join(texto_parrafo_limpio)
            
            
            lista_palabras_parrafo, lista_palabras_cita = TextProcessor.obtain_list_english_words(texto_parrafo, texto_cita_limpio_string)
            start_time = time.perf_counter()
            num_coincidencias = processor.longestCommonSubseq(lista_palabras_parrafo, lista_palabras_cita)
            end_time = time.perf_counter()

            if num_coincidencias > max_coincidencias:
                mejor_parrafo = texto
                max_coincidencias = num_coincidencias
                mejor_citas = citas
        
        # print("el parrafo con mas coincidencias es: ", mejor_parrafo)
        print("Tiempo de ejecución:", end_time - start_time, "segundos")
        bibliografia_completa = ""  # Inicializar el string de la bibliografía
        # si contiene la cita, extraigo las citas del parrafo correspondiente al texto que ha seleccionado el usuario
        citas_seleccionadas = TextProcessor.extraer_citas(mejor_parrafo)
        # print("Las citas del parrafo son: ", citas_seleccionadas)
        # ahora en citas_seleccionadas, estan las citas que ha seleccionado el usuario al seleccionar texto en el párrafo
        #ahora las contrasto con las citas que aparecen en el parrfo correspondiente a la seleccion
        # print("Todas las citas del parrafo son: ", mejor_citas)
        for cita in citas_seleccionadas:
            # Obtener el identificador de la cita
            identificador = cita.split(":")[1].split("}")[0]
            # print("la cita seleccionada es: ", identificador)
            # print("hasta aqui la cita selecionada")
            
            if any(identificador == span["ref_id"] for span in mejor_citas):
                # Construir el string de la bibliografía
                bibliografia_completa += f"Cita {{cite:{identificador}}}\n"
                # en caso de que exista, hay que ir a buscarla a las referencias
                bibliografia_raw = bibliografia[identificador]["bib_entry_raw"]
                bibliografia_completa += f"Bibliografía: {bibliografia_raw}\n\n"
            else:
                bibliografia_completa += f"La cita {{cite:{cita}}} no coincide con ninguna cita en obj.\n"
        
        return {"bibliografia": bibliografia_completa, "parrafo_cita": mejor_parrafo}


    # Implementado con kmp
    # def obtener_bibliografia_texto_parrafo_seleccion(self, index_name, paper_id, cita):
    #     consulta = {"query": {"match": {"paper_id": paper_id}}}   
    #     # Realizar la consulta para obtener el documento específico
    #     resultado = self.client.search(index=index_name, body=consulta)
    #     # Obtener el documento específico de los resultados
    #     documento_especifico = resultado["hits"]["hits"][0]["_source"]

    #     # Acceder al campo json_data para obtener el documento serializado
    #     documento_serializado = documento_especifico["json_data"]

    #     # Deserializar el documento serializado para obtener el documento original
    #     documento_original = json.loads(documento_serializado)

    #     # Acceder al campo body_text del documento original
    #     body_text = documento_original["body_text"]
    #     # cojo las referencias de las citas del documento original
    #     bibliografia = documento_original["bib_entries"]

    #     #para almacenar el parrafo en el que se encuentra la cita
    #     parrafo_cita = ""

    #     bibliografia_completa = ""  # Inicializar el string de la bibliografía

    #     mejor_parrafo = ""
    #     max_coincidencias = 0   
    #     mejor_citas = []

    #     processor = TextProcessor()
    #     texto_cita_limpio = processor.limpiar_texto(cita)
    #     texto_cita_limpio_string = ' '.join(texto_cita_limpio)
    #     for obj in body_text:
    #         # cojo el parrafo
    #         texto = obj["text"]
    #         # cojo las citas del parrafo
    #         citas = obj["cite_spans"]
    #         # print("Las citas de cada parrafo son: ", citas)
    #         # esto habrá que sustiruirlo por el algoritmo nuevo implementado, convirtiendoi primero texto_cita_limpio y 
    #         # texto_parrafo_limpio en listas, con la funcion obtain_list_english_words, y luego comparando si está en el párrafo con el algoritmo

    #         # Tengo que moidificar esto para que en vez de coger texto tal cual de la cita, primero lo tokenice, y lo compare con los párrafos, necesitando un 90% de coincnidencia entre las palabras, por si la selección de la cita, se come algo del principio o del final de una palabra
    #         texto_parrafo_limpio = processor.limpiar_texto(texto)
    #         # print("ha llamado a text_processor bien")
    #         texto_parrafo = ' '.join(texto_parrafo_limpio)

    #         lista_palabras_parrafo, lista_palabras_cita = TextProcessor.obtain_list_english_words(texto_parrafo, texto_cita_limpio_string)
    #         start_time = time.perf_counter()
    #         num_coincidencias = processor.longestCommonSubseq_KMP(lista_palabras_parrafo, lista_palabras_cita)
    #         end_time = time.perf_counter()
    #         if num_coincidencias > max_coincidencias:
    #             mejor_parrafo = texto
    #             max_coincidencias = num_coincidencias
    #             mejor_citas = citas
    #     # Imprime el resultado y el tiempo de ejecución
    #     print("Tiempo de ejecución:", end_time - start_time, "segundos")
    #     bibliografia_completa = ""  # Inicializar el string de la bibliografía
    #     # si contiene la cita, extraigo las citas del parrafo correspondiente al texto que ha seleccionado el usuario
    #     citas_seleccionadas = TextProcessor.extraer_citas(mejor_parrafo)
    #     # print("Las citas del parrafo son: ", citas_seleccionadas)
    #     # ahora en citas_seleccionadas, estan las citas que ha seleccionado el usuario al seleccionar texto en el párrafo
    #     #ahora las contrasto con las citas que aparecen en el parrfo correspondiente a la seleccion
    #     # print("Todas las citas del parrafo son: ", mejor_citas)
    #     for cita in citas_seleccionadas:
    #         # Obtener el identificador de la cita
    #         identificador = cita.split(":")[1].split("}")[0]
    #         # print("la cita seleccionada es: ", identificador)
    #         # print("hasta aqui la cita selecionada")
            
    #         if any(identificador == span["ref_id"] for span in mejor_citas):
    #             # Construir el string de la bibliografía
    #             bibliografia_completa += f"Cita {{cite:{identificador}}}\n"
    #             # en caso de que exista, hay que ir a buscarla a las referencias
    #             bibliografia_raw = bibliografia[identificador]["bib_entry_raw"]
    #             bibliografia_completa += f"Bibliografía: {bibliografia_raw}\n\n"
    #         else:
    #             bibliografia_completa += f"La cita {{cite:{cita}}} no coincide con ninguna cita en obj.\n"
        
    #     return {"bibliografia": bibliografia_completa, "parrafo_cita": mejor_parrafo}

    def obtener_tokens_cuerpo(self, index_name, paper_id_obtener, archivo_destino): 
        resultado = self.client.search(
            index=index_name,
            body={
                "query": {
                    "match": {
                        "paper_id": paper_id_obtener
                    }
                }
            }
        )
        print("El id del docukento que se esta buscando es:", paper_id_obtener)
        hits = resultado["hits"]["hits"]
        if hits: 
            tokens_texto = []
            documento_especifico = hits[0]["_source"]
            # Acceder al campo json_data para obtener el documento serializado
            documento_serializado = documento_especifico["json_data"]

            # Deserializar el documento serializado para obtener el documento original
            documento_original = json.loads(documento_serializado)

            # Acceder al campo body_text del documento original
            body_text = documento_original["body_text"]

            for obj in body_text:
                # cojo el parrafo
                texto = obj["text"]
                texto_parrafo_limpio = self.text_processor.limpiar_texto(texto)
                texto_parrafo = ' '.join(texto_parrafo_limpio)
                tokens_obtenidos = self.text_processor.obtain_list_english_words_from_body(texto_parrafo)
                tokens_texto += tokens_obtenidos
            return tokens_texto
        else:
            print("como no se ha encontrado el documento en la base de datos, lo descargo y extraigo el texto")
            # Si el paper_id no se encuentra en la base de datos, descargar y extraer el PDF
            texto_pdf, _ = PDFProcessor.descargar_y_extraer_texto_pdf_arxiv(paper_id_obtener, "../datos/")
            texto_parrafo_limpio = self.text_processor.limpiar_texto(texto_pdf)
            texto_parrafo = ' '.join(texto_parrafo_limpio)
            print(type(texto_parrafo)) 
            tokens_obtenidos = self.text_processor.obtain_list_english_words_from_body(texto_parrafo)
            return tokens_obtenidos


    # Funcion para obtener los paper_id de los primeros 10 documentos y los ultimos 10 documentos de index_name
    def obtener_paper_ids(self, index_name):
        n1, n2 = 2, 2
        # Consulta para obtener los primeros 10 documentos del índice
        resultados_principio = self.client.search(
            index=index_name,
            body={
                "size": n1,  # Recuperar 10 documentos
                "query": {
                    "match_all": {}  # Coincidir con todos los documentos
                }
            }
        )
        
        # Consulta para obtener los últimos 10 documentos del índice
        resultados_final = self.client.search(
            index=index_name,
            body={
                "size": n2,  # Recuperar 10 documentos
                "query": {
                    "match_all": {}  # Coincidir con todos los documentos
                },
                "sort": [
                    {"_id": {"order": "desc"}}  # Ordenar por identificador de documento en orden descendente
                ]
            }
        )
        
        # Extraer los paper_id de los primeros 10 documentos
        paper_ids_principio = [hit["_source"]["paper_id"] for hit in resultados_principio["hits"]["hits"]]
        
        # Extraer los paper_id de los últimos 10 documentos
        paper_ids_final = [hit["_source"]["paper_id"] for hit in resultados_final["hits"]["hits"]]
        
        return paper_ids_principio, paper_ids_final


    
