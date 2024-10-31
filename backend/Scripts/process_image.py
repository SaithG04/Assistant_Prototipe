# import tensorflow as tf
# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import io
import os

from tensorflow.keras.applications import MobileNetV2
import numpy as np
from PIL import Image, ImageFilter, ImageStat
import logging
from io import BytesIO
import cv2
from cv2 import dnn_superres

# Cargar el modelo al inicio
model = MobileNetV2(weights='imagenet')
def classify_image(image_file):
    try:
        # Convertir la imagen de BytesIO a un arreglo numpy
        image = Image.open(image_file)
        image = image.resize((224, 224))  # Ajusta el tamaño según el modelo de TensorFlow
        image_array = np.array(image)  # Convertir la imagen a un arreglo Numpy

        # Verificar si la imagen tiene 3 canales (RGB)
        if len(image_array.shape) == 2:  # Convertir imágenes en escala de grises a RGB
            image_array = np.stack([image_array] * 3, axis=-1)

        # Normalizar los valores de los píxeles entre 0 y 1
        image_array = image_array / 255.0

        # Pasar la imagen al modelo de clasificación
        # Aquí usarías tu modelo de TensorFlow para clasificar la imagen
        prediction = model.predict(
            np.expand_dims(image_array, axis=0))  # Asegúrate de que el modelo esté cargado correctamente
        predicted_class = np.argmax(prediction)

        # Según la clase predicha, puedes devolver el tipo de imagen (matemática, no matemática, etc.)
        if predicted_class == 0:
            return "mathematics"
        else:
            return "other"
    except Exception as e:
        logging.error(f"Error clasificando la imagen: {str(e)}")
        return "error"

def preprocess_image(image_file):
    image = Image.open(image_file).convert('L')  # Escala de grises
    image = image.filter(ImageFilter.SHARPEN)  # Aplicar un filtro de nitidez
    image = image.resize((image.width * 2, image.height * 2))  # Aumentar el tamaño
    image = image.point(lambda p: p > 128 and 255)  # Binarización
    return image


def preprocess_image_to_bw(image_file):
    # Abrir la imagen con PIL y convertirla a escala de grises
    image = Image.open(image_file).convert('L')

    # Convertir la imagen a un array de numpy para usar OpenCV
    image_np = np.array(image)

    # Aplicar el umbral de Otsu para binarizar la imagen (blanco y negro)
    _, bw_image = cv2.threshold(image_np, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Convertir de vuelta a PIL para usarla en OCR
    return Image.fromarray(bw_image)

def convert_image_to_bytes(image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')  # Guardar la imagen preprocesada como bytes
    img_byte_arr.seek(0)  # Volver al inicio del stream de bytes
    return img_byte_arr


def is_image_blank(image_file):
    image = Image.open(image_file).convert("L")  # Convertir a escala de grises
    stat = ImageStat.Stat(image)
    mean_brightness = stat.mean[0]  # Promedio de brillo de la imagen

    # Si el brillo está muy cerca de 255 (completamente blanco), consideramos que la imagen está vacía
    if mean_brightness > 250:
        return True
    return False


def improve_image_resolution(image_file):
    # Leer la imagen en formato OpenCV
    image = Image.open(image_file)
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # image = image.resize((image.width // 2, image.height // 2))  # Reducir al 50%

    # Cargar el modelo de super-resolución DNN en OpenCV
    sr = dnn_superres.DnnSuperResImpl_create()
    model_path = os.path.abspath("./models/ESPCN_x4.pb")
    sr.readModel(model_path)
    sr.setModel("espcn", 4)  # Configurar el modelo para 4x la resolución original

    # Aumentar la resolución
    result = sr.upsample(image)

    # Convertir el resultado a formato RGB y guardarlo en un BytesIO para enviarlo como respuesta
    result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    result_image = Image.fromarray(result)
    img_io = io.BytesIO()
    result_image.save(img_io, format="JPEG")
    img_io.seek(0)

    return img_io