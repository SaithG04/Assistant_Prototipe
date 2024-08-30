from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import json

# Cargar el modelo entrenado
def cargar_modelo(model_path='modelo_clasificador.h5'):
    return load_model(model_path)

# Cargar el tokenizer
def cargar_tokenizer(tokenizer_path='tokenizer.json'):
    with open(tokenizer_path, 'r') as f:
        json_string = f.read()  # Cargar el contenido como cadena
        tokenizer = tokenizer_from_json(json_string)
    return tokenizer