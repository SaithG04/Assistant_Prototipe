import json
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from sklearn.model_selection import train_test_split

def entrenar_modelo():
    # Cargar los datos
    X = np.load('secuencias_busqueda.npy')
    y = np.load('labels_busqueda.npy')

    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Crear el modelo
    model = Sequential()
    model.add(Embedding(input_dim=5000, output_dim=128, input_length=X.shape[1]))
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
    model.save('modelo_busqueda.h5')

    print("Modelo guardado exitosamente.")

if __name__ == "__main__":
    entrenar_modelo()