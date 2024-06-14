import torch
from transformers import AutoTokenizer, AutoModel
from model import FNN

def load_model(model_path, base_model_path, method_name="fnn"):
    # Cargar el tokenizador y el modelo base
    tokenizer = AutoTokenizer.from_pretrained(base_model_path, add_prefix_space=True)
    base_model = AutoModel.from_pretrained(base_model_path)

    # Inicializar el modelo específico
    if method_name == "fnn":
        model = FNN(base_model, 3)  # Asegúrate de definir num_classes
    else:
        raise ValueError("Método desconocido")

    # Cargar pesos entrenados
    model_state_dict = torch.load(model_path, map_location=torch.device('cpu'))
    model.base_model.embeddings.word_embeddings.weight.data = model_state_dict['base_model.embeddings.word_embeddings.weight']
    model.load_state_dict(model_state_dict, strict=False)

    # Mover el modelo a la GPU si está disponible
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Poner el modelo en modo de evaluación
    model.eval()

    return model, tokenizer

def predict_polarity(model, tokenizer, text, device):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)
    return predict_polarity_from_inputs(model, {"input_ids": input_ids, "attention_mask": attention_mask})

def predict_polarity_from_inputs(model, inputs):
    with torch.no_grad():
        probabilities = model(inputs)
    return probabilities.cpu().numpy()




if __name__ == "__main__":
    model_path = "../datos/pesos_modelo.pt"  # Ajusta la ruta según donde hayas guardado el modelo
    base_model_path = "bert-base-uncased"  # Ruta al modelo base utilizado durante el entrenamiento
    model, tokenizer = load_model(model_path, base_model_path, method_name="fnn")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # Definir device aquí

    text = "Tu texto aquí para analizar la polaridad"
    probabilities = predict_polarity(model, tokenizer, text, device)

    print("Probabilidades:", probabilities)
