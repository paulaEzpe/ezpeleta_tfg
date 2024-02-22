from flask import Flask, request

app = Flask(__name__)

@app.route("/uploadText", methods=["POST"])
def upload_text():
    data = request.json
    pdf_text = data.get('pdfText')
    if pdf_text is None:
        return {"error": "No se proporcionó el texto del PDF"}, 400
    else:
        # guardar el texto recibido en un txt
        with open('pdf_text.txt', 'w') as file:
            file.write(pdf_text)
        
        return {"message": "Texto del PDF recibido y guardado exitosamente en pdf_text.txt."}
    

if __name__ == "__main__":
    app.run(debug=True)
