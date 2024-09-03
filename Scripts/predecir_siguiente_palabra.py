import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json

# Cargar el modelo entrenado
model = load_model('modelo_chat_grande.h5')

# Cargar el tokenizer
with open('tokenizer_chat_grande.json', 'r', encoding='utf-8') as f:
    tokenizer_data = json.load(f)
    tokenizer = tokenizer_from_json(json.dumps(tokenizer_data))


# Función para predecir la siguiente palabra
def predecir_siguiente_palabra(texto):
    secuencia = tokenizer.texts_to_sequences([texto])
    secuencia_padded = pad_sequences(secuencia, maxlen=model.input_shape[1], padding='post')

    prediccion = model.predict(secuencia_padded)
    siguiente_palabra_index = np.argmax(prediccion)

    # Convertir el índice de vuelta a texto
    palabra_siguiente = tokenizer.index_word.get(siguiente_palabra_index, '')
    return palabra_siguiente


# Ejemplo de uso
if __name__ == "__main__":
    texto = input("Tú: ")
    while texto.lower() != "salir":
        siguiente_palabra = predecir_siguiente_palabra(texto)
        print(f"Asistente: {siguiente_palabra}")
        texto = input("Tú: ")
