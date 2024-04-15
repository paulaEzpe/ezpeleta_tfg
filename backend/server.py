# from flask import Flask, request

# app = Flask(__name__)

# @app.route("/uploadText", methods=["POST"])
# def upload_text():
#     data = request.json
#     # Para recibir el pdf
#     pdf_text = data.get('pdfText')
#     # Para extraer el texto del input
#     input_text = data.get('inputText')  # Obtener el texto del input
    
#     if pdf_text is None:
#         return {"error": "No se proporcionó el texto del PDF"}, 400
#     else:
#         # Guardar el texto recibido en un txt
#         with open('pdf_text.txt', 'w') as file:
#             file.write(pdf_text)
        
#         # Mostrar el texto del input por terminal
#         print("Texto del input:", input_text)
        
#         return {"message": "Texto del PDF recibido y guardado exitosamente en pdf_text.txt."}

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, request

app = Flask(__name__)


# Para recibir el pdf 
@app.route("/uploadPDFText", methods=["POST"])
def upload_pdf_text():
    data = request.json
    pdf_text = data.get('pdfText')
    if pdf_text is None:
        return {"error": "No se proporcionó el texto del PDF"}, 400
    else:
        # Guardar el texto del PDF recibido en un archivo txt
        with open('pdf_text.txt', 'w') as file:
            file.write(pdf_text)
        return {"message": "Texto del PDF recibido y guardado exitosamente en pdf_text.txt."}

# Para recibir el input de la cuarta opcion del accordion
@app.route("/uploadInputText", methods=["POST"])
def upload_input_text():
    data = request.json
    input_text = data.get('inputText')
    if input_text is None:
        return {"error": "No se proporcionó el texto del input"}, 400
    else:
        # Mostrar el texto del input en la terminal
        print("Texto del input recibido:", input_text)
        return {"message": "Texto del input recibido y mostrado en la terminal."}


@app.route("/uploadSelectedText", methods=["POST"])
def save_selected_text():
    data = request.json
    selected_text = data.get('selectedText')
    if selected_text is None:
        return {"error": "No se proporcionó texto seleccionado"}, 400
    else:
        # Mostrar el texto seleccionado en la terminal
        print('Texto seleccionado:', selected_text)
        return {"message": "Texto seleccionado recibido y mostrado en la terminal."}



if __name__ == "__main__":
    app.run(debug=True)
