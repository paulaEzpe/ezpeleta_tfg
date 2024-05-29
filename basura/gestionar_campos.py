import os
import json
import re

#https://stackoverflow.com/questions/4578912/replace-all-accented-characters-by-their-latex-equivalent
#######################################
latexAccents = [
  [ u"à", "\\`a" ], # Grave accent
  [ u"è", "\\`e" ],
  [ u"ì", "\\`\\i" ],
  [ u"ò", "\\`o" ],
  [ u"ù", "\\`u" ],
  [ u"ỳ", "\\`y" ],
  [ u"À", "\\`A" ],
  [ u"È", "\\`E" ],
  [ u"Ì", "\\`\\I" ],
  [ u"Ò", "\\`O" ],
  [ u"Ù", "\\`U" ],
  [ u"Ỳ", "\\`Y" ],
  [ u"á", "\\'a" ], # Acute accent
  [ u"é", "\\'e" ],
  [ u"í", "\\'\\i" ],
  [ u"ó", "\\'o" ],
  [ u"ú", "\\'u" ],
  [ u"ý", "\\'y" ],
  [ u"Á", "\\'A" ],
  [ u"É", "\\'E" ],
  [ u"Í", "\\'\\I" ],
  [ u"Ó", "\\'O" ],
  [ u"Ú", "\\'U" ],
  [ u"Ý", "\\'Y" ],
  [ u"â", "\\^a" ], # Circumflex
  [ u"ê", "\\^e" ],
  [ u"î", "\\^\\i" ],
  [ u"ô", "\\^o" ],
  [ u"û", "\\^u" ],
  [ u"ŷ", "\\^y" ],
  [ u"Â", "\\^A" ],
  [ u"Ê", "\\^E" ],
  [ u"Î", "\\^\\I" ],
  [ u"Ô", "\\^O" ],
  [ u"Û", "\\^U" ],
  [ u"Ŷ", "\\^Y" ],
  [ u"ä", "\\\"a" ],    # Umlaut or dieresis
  [ u"ë", "\\\"e" ],
  [ u"ï", "\\\"\\i" ],
  [ u"ö", "\\\"o" ],
  [ u"ü", "\\\"u" ],
  [ u"ÿ", "\\\"y" ],
  [ u"Ä", "\\\"A" ],
  [ u"Ë", "\\\"E" ],
  [ u"Ï", "\\\"\\I" ],
  [ u"Ö", "\\\"O" ],
  [ u"Ü", "\\\"U" ],
  [ u"Ÿ", "\\\"Y" ],
  [ u"ç", "\\c{c}" ],   # Cedilla
  [ u"Ç", "\\c{C}" ],
  [ u"œ", "{\\oe}" ],   # Ligatures
  [ u"Œ", "{\\OE}" ],
  [ u"æ", "{\\ae}" ],
  [ u"Æ", "{\\AE}" ],
  [ u"å", "{\\aa}" ],
  [ u"Å", "{\\AA}" ],
  [ u"–", "--" ],   # Dashes
  [ u"—", "---" ],
  [ u"ø", "{\\o}" ],    # Misc latin-1 letters
  [ u"Ø", "{\\O}" ],
  [ u"ß", "{\\ss}" ],
  [ u"¡", "{!`}" ],
  [ u"¿", "{?`}" ],
  [ u"\\", "\\\\" ],    # Characters that should be quoted
  [ u"~", "\\~" ],
  [ u"&", "\\&" ],
  [ u"$", "\\$" ],
  [ u"{", "\\{" ],
  [ u"}", "\\}" ],
  [ u"%", "\\%" ],
  [ u"#", "\\#" ],
  [ u"_", "\\_" ],
  [ u"≥", "$\\ge$" ],   # Math operators
  [ u"≤", "$\\le$" ],
  [ u"≠", "$\\neq$" ],
  [ u"©", "\copyright" ], # Misc
  [ u"ı", "{\\i}" ],
  [ u"µ", "$\\mu$" ],
  [ u"°", "$\\deg$" ],
  [ u"‘", "`" ],    #Quotes
  [ u"’", "'" ],
  [ u"“", "``" ],
  [ u"”", "''" ],
  [ u"‚", "," ],
  [ u"„", ",," ],
]

#-------------------------------------------------

# Cambia códigos de latex a su representación en unicode
def normaliza(tabla,texto):
    normalizado = texto
    for [unicode,latex] in tabla:
        normalizado = normalizado.replace(latex,unicode)
    return normalizado

#---------------------------------------------------

def medir_carpeta(carpeta):
    files = [f for f in os.listdir(carpeta)]
    contados = 0
    print(carpeta)
    for f in files:
        print(f)
        nombre = carpeta + f 
        print(str(nombre))
        contados += medir_tamano_ref_entries(nombre, "ref_entries.txt")
    print("json con ref_entries contados: " + str(contados))

#---------------------------------------------------

def medir_tamano_ref_entries(json_file, output_file):
    # Abre el archivo JSONL de entrada y el archivo de salida
    with open(json_file, "r") as f_input, open(output_file, "w") as f_output:
        datos = f_input.readlines()
        i = 0
        for line in datos:
            # Carga el JSON de la línea actual
            line_json = json.loads(line)
            ref_entries = line_json["ref_entries"]
            # Escribe el campo ref_entries en el archivo de salida
            f_output.write(json.dumps(ref_entries) + "\n")
            i += 1
            print("i: " + str(i))
    print("Data inserted successfully.")
    return i

#-----------------------------------------------

def extraer_campos_indice(json_file):
    with open(json_file, "r") as f_input:
        datos = f_input.readlines()
        i = 0
        for line in datos:
            # Carga el JSON de la línea actual
            line_json = json.loads(line)
            # Extraer campos para indice
            _id = line_json["paper_id"]
            disciplina = line_json["discipline"]
            titulo = line_json["metadata"]["title"]
            titulo = titulo.replace("\n", " " if titulo.endswith(" ") else "")
            titulo = re.sub(r' {2,}', ' ', titulo)
            titulo = normaliza(latexAccents, titulo)
            categoria = line_json["metadata"]["categories"]
            autores = line_json["metadata"]["authors"]
            autores = autores.replace("\n", " " if autores.endswith(" ") else "")
            autores = re.sub(r' {2,}', ' ', autores)
            autores = normaliza(latexAccents, autores)
            i += 1
            print("i: " + str(i))
            print("_id:", _id)
            print("disciplina:", disciplina)
            print("título:", titulo)
            print("categoría:", categoria)
            print("autores:", autores)

#################################################################

#medir_carpeta("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/unarXive_230324_open_subset/08/")
extraer_campos_indice("arXiv_src_2201_009.jsonl")
