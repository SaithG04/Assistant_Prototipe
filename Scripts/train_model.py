import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Cargar los datos desde un archivo JSON
def cargar_datos_json(filename='datos.json'):
    with open(filename, 'r') as file:
        datos = json.load(file)
    titulos = [item['title'] for item in datos]
    urls = [item['url'] for item in datos]
    labels = [item['label'] for item in datos]  # 1 para correcto, 0 para incorrecto
    return titulos, urls, labels

def entrenar_modelo(titulos, labels):
    # Preprocesamiento de texto
    tokenizer = Tokenizer(num_words=5000, lower=True)
    tokenizer.fit_on_texts(titulos)
    X = tokenizer.texts_to_sequences(titulos)
    X = pad_sequences(X, maxlen=50)

    # Codificación de las etiquetas
    encoder = LabelEncoder()
    y = encoder.fit_transform(labels)

    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Crear el modelo
    model = Sequential()
    model.add(Embedding(input_dim=5000, output_dim=128, input_length=50))
    model.add(SpatialDropout1D(0.2))
    model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(1, activation='sigmoid'))

    # Compilar el modelo
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Entrenar el modelo
    model.fit(X_train, y_train, epochs=5, batch_size=64, validation_data=(X_test, y_test), verbose=1)

    # Evaluación
    score, acc = model.evaluate(X_test, y_test, verbose=2)
    print(f'Test accuracy: {acc}')

    # Guardar el modelo
    model.save('modelo_clasificador.h5')

    # Guardar el tokenizer para preprocesar nuevas entradas
    with open('tokenizer.json', 'w') as f:
        f.write(tokenizer.to_json())

    print("Modelo y tokenizer guardados exitosamente.")

# Cargar los datos y entrenar el modelo
titulos, urls, labels = cargar_datos_json('datos.json')
entrenar_modelo(titulos, labels)