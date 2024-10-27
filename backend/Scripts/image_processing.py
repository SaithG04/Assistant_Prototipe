import cv2
import numpy as np
from PIL import Image
from io import BytesIO


def process_image_for_edges(image_stream):
    """
    Procesa una imagen para detectar bordes usando el algoritmo de Canny.

    :param image_stream: Archivo de imagen en formato stream.
    :return: Imagen procesada en formato stream (BytesIO).
    """
    # Convertir la imagen a un objeto PIL
    img = Image.open(image_stream).convert('RGB')

    # Convertir la imagen a un arreglo NumPy
    img_array = np.array(img)

    # Convertir la imagen a escala de grises
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # Aplicar detección de bordes (Canny)
    edges = cv2.Canny(gray, threshold1=100, threshold2=200)

    # Convertir el resultado a una imagen PIL
    result_image = Image.fromarray(edges)

    # Guardar la imagen procesada en un buffer en memoria
    img_io = BytesIO()
    result_image.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io
