

import PyPDF2
import re
#-------------------------------------------
def extraer_texto_pdf(ruta_pdf):
        texto = ""
        with open(ruta_pdf, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                texto += page.extract_text()
        return texto
#-------------------------------------------
#devuelve una lista de párrafo. Consideramos que un ".", seguido de 
#uno o más saltos de línea, seguido de una mayúsucla, es un párrafo
def procesa_cuerpo(cuerpo):
    parrafos = []
    patt = re.compile("([^\n]+)\.\n+")
    parrafos = re.split(patt,cuerpo)
    parrafos = [p.replace('-\n','').replace('\n',' ') for p in parrafos]
    return parrafos
     
#-------------------------------------------
fuentes = ["1104.1114.pdf", "2002.11023.pdf"
    ]

textos = []
for f in fuentes:
    nomFich = "../datos/" + f
    texto = extraer_texto_pdf(nomFich)
    textos.append(texto)
    with open(nomFich + '.txt', 'w') as file:
         file.write(texto)
        
for texto in textos:
    r1 = '((.|\n)+)'
    r2 = '[Aa][Bb][Ss][Tt][Rr][Aa][Cc][Tt]'
    r3 = '((.|\n)+?)'
    r4 = '[Ii][Nn][Tt][Rr][Oo][Dd][Uu][Cc][Tt][Ii][Oo][Nn]'
    r5 = '((.|\n)+)'
    result = re.search(r1 + r2 + r3 + r4 + r5, texto)
    if result:
        #parece que pre_abstract y abstract están en los grupos 1 y 3, respectivamente
        pre_abstract = result.group(1)
        abstract = result.group(3)
        cuerpo = result.group(5)
        print("pre-abstract ***************")
        print(pre_abstract)
        print("abstract *******************")
        print(abstract)
        print("cuerpo *******************")
        print(cuerpo)
        

