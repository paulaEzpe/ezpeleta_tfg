import json

def contar_campos_jsonl(archivo):
    campos = set()

    with open(archivo, "r") as f:
        for linea in f:
            datos = json.loads(linea)
            campos.update(datos.keys())

    return len(campos)

archivo_jsonl = "un_json.jsonl"
cantidad_campos = contar_campos_jsonl(archivo_jsonl)
print("Número total de campos en el archivo JSONL:", cantidad_campos)
