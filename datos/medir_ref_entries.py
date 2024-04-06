import os
import json


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

medir_carpeta("/home/paula/Documentos/CUARTO_INF/SEGUNDO_CUATRI/tfg/unarXive_230324_open_subset/08/")