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

        contiene_cita = False
        bibliografia_completa = ""  # Inicializar el string de la bibliografía

        mejor_parrafo = None
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
            print("Las citas de cada parrafo son: ", citas)
            # esto habrá que sustiruirlo por el algoritmo nuevo implementado, convirtiendoi primero texto_cita_limpio y 
            # texto_parrafo_limpio en listas, con la funcion obtain_list_english_words, y luego comparando si está en el párrafo con el algoritmo

            # Tengo que moidificar esto para que en vez de coger texto tal cual de la cita, primero lo tokenice, y lo compare con los párrafos, necesitando un 90% de coincnidencia entre las palabras, por si la selección de la cita, se come algo del principio o del final de una palabra
            texto_parrafo_limpio = processor.limpiar_texto(texto)
            # print("ha llamado a text_processor bien")
            texto_parrafo = ' '.join(texto_parrafo_limpio)
            
            
            lista_palabras_parrafo, lista_palabras_cita = TextProcessor.obtain_list_english_words(texto_parrafo, texto_cita_limpio_string)
            num_coincidencias = processor.longestCommonSubseq(lista_palabras_parrafo, lista_palabras_cita)
            if num_coincidencias > max_coincidencias:
                mejor_parrafo = texto
                max_coincidencias = num_coincidencias
                mejor_citas = citas
        
        print("el parrafo con mas coincidencias es: ", mejor_parrafo)
        bibliografia_completa = ""  # Inicializar el string de la bibliografía
        # si contiene la cita, extraigo las citas del parrafo correspondiente al texto que ha seleccionado el usuario
        citas_seleccionadas = TextProcessor.extraer_citas(mejor_parrafo)
        print("Las citas del parrafo son: ", citas_seleccionadas)
        # ahora en citas_seleccionadas, estan las citas que ha seleccionado el usuario al seleccionar texto en el párrafo
        #ahora las contrasto con las citas que aparecen en el parrfo correspondiente a la seleccion
        print("Todas las citas del parrafo son: ", mejor_citas)
        for cita in citas_seleccionadas:
            # Obtener el identificador de la cita
            identificador = cita.split(":")[1].split("}")[0]
            print("la cita seleccionada es: ", identificador)
            print("hasta aqui la cita selecionada")
            
            if any(identificador == span["ref_id"] for span in obj["cite_spans"]):
                # Construir el string de la bibliografía
                bibliografia_completa += f"Cita {{cite:{identificador}}}\n"
                # en caso de que exista, hay que ir a buscarla a las referencias
                bibliografia_raw = bibliografia[identificador]["bib_entry_raw"]
                bibliografia_completa += f"Bibliografía: {bibliografia_raw}\n\n"
            else:
                bibliografia_completa += f"La cita {{cite:{cita}}} no coincide con ninguna cita en obj.\n"
        
        return {"bibliografia": bibliografia_completa, "parrafo_cita": mejor_parrafo}