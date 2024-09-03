import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, SpatialDropout1D
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import json

# Cargar las secuencias preparadas
secuencias = np.load('secuencias_chat_grande.npy')

# Cargar el tokenizer desde el archivo JSON
with open('tokenizer_chat_grande.json', 'r', encoding='utf-8') as f:
    tokenizer_data = json.load(f)

# Crear el tokenizer desde la cadena JSON
tokenizer = tokenizer_from_json(json.dumps(tokenizer_data))

vocab_size = len(tokenizer.word_index) + 1

# Crear el modelo
model = Sequential()
model.add(Embedding(input_dim=vocab_size, output_dim=128, input_length=secuencias.shape[1]))
model.add(SpatialDropout1D(0.2))
model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(vocab_size, activation='softmax'))

# Compilar el modelo
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Ajustar las secuencias de respuestas para predecir la siguiente palabra
X = secuencias[:, :-1]
y = secuencias[:, -1]

# Entrenar el modelo
model.fit(X, y, epochs=10, batch_size=64, validation_split=0.2, verbose=1)

# Guardar el modelo entrenado y el tokenizer
model.save('modelo_chat_grande.h5')

print("Modelo de chat entrenado y guardado exitosamente.")