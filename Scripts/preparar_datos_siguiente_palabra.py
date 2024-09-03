import json
import numpy as np
from keras.src.legacy.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import tqdm
import os
import signal

# Verificar si las stopwords están disponibles
try:
    _ = stopwords.words('spanish')
except LookupError:
    nltk.download('stopwords')

# Variables globales para manejo de interrupción
tokenizer = None
secuencias = []
progreso_guardado = False

def guardar_progreso(tokenizer, secuencias):
    """Función para guardar el progreso del tokenizer y las secuencias."""
    global progreso_guardado
    np.save('secuencias_chat_grande_temp.npy', np.array(secuencias, dtype=object))
    with open('tokenizer_chat_grande_temp.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(tokenizer.to_json(), ensure_ascii=False))
    print(f"\nProgreso guardado. Chunks procesados: {len(secuencias)} secuencias guardadas.")
    progreso_guardado = True

def signal_handler(sig, frame):
    """Manejador para la señal de interrupción."""
    print("\nInterrupción detectada. Guardando progreso antes de salir...")
    guardar_progreso(tokenizer, secuencias)
    print("Progreso guardado. Saliendo del programa.")
    exit(0)

# Conectar la señal de interrupción al manejador
signal.signal(signal.SIGINT, signal_handler)

# Reducir el tamaño del chunk para pruebas más rápidas
def leer_archivo_en_chunks(ruta_archivo, tamaño_chunk=1024 * 512):  # Tamaño de chunk reducido
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        while True:
            chunk = archivo.read(tamaño_chunk)
            if not chunk:
                break
            yield chunk

def preprocesar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúñü\s]', '', texto)  # Eliminar caracteres no deseados
    palabras = word_tokenize(texto)  # Tokenizar usando nltk
    palabras = [palabra for palabra in palabras if palabra not in stopwords.words('spanish') and palabra not in string.punctuation]
    return ' '.join(palabras)

def preparar_datos(ruta_archivo, tokenizer, maxlen=50):
    global secuencias
    for chunk in tqdm.tqdm(leer_archivo_en_chunks(ruta_archivo), desc="Procesando chunks"):
        texto_procesado = preprocesar_texto(chunk)
        secuencia = tokenizer.texts_to_sequences([texto_procesado])
        secuencias_padded = pad_sequences(secuencia, maxlen=maxlen, padding='post')
        secuencias.extend(secuencias_padded)

        # Guardar el progreso después de cada chunk
        guardar_progreso(tokenizer, secuencias)

    return np.array(secuencias)

def cargar_o_entrenar_tokenizer(ruta_archivo, tokenizer_path='tokenizer_chat_grande_temp.json'):
    global tokenizer
    if os.path.exists(tokenizer_path):
        print("Cargando tokenizer existente...")
        with open(tokenizer_path, 'r', encoding='utf-8') as f:
            tokenizer_data = json.load(f)
        tokenizer = tokenizer_from_json(tokenizer_data)
    else:
        tokenizer = Tokenizer(num_words=5000, lower=True, split=' ')
        print("Entrenando el tokenizer...")
        for chunk in tqdm.tqdm(leer_archivo_en_chunks(ruta_archivo), desc="Entrenando tokenizer"):
            texto_procesado = preprocesar_texto(chunk)
            tokenizer.fit_on_texts([texto_procesado])
        with open(tokenizer_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(tokenizer.to_json(), ensure_ascii=False))
    return tokenizer

ruta_archivo = '../files/eswiki-latest-pages-articles.txt'

# Cargar o entrenar el tokenizer
tokenizer = cargar_o_entrenar_tokenizer(ruta_archivo)

# Preparar secuencias con guardado periódico
print("Preparando secuencias...")
secuencias = preparar_datos(ruta_archivo, tokenizer)

# Guardar las secuencias completas en archivos .npy
np.save('secuencias_chat_grande.npy', secuencias)

print("El tokenizer y las secuencias han sido creados y guardados exitosamente.")