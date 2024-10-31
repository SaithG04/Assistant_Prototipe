import re
import logging
from PIL import ImageStat, Image

# Diccionario de traducción de días de la semana
day_translation = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

def preprocess_text(text):
    """
    Preprocesa el texto para asegurarse de que sea adecuado para Gemini, eliminando caracteres innecesarios.
    """
    # Limitar el texto a alfabeto básico, números y operadores matemáticos
    text = re.sub(r'[^a-zA-Z0-9\s+\-*/=]', '', text)
    return text.strip()


def sanitize_response(response_text):
    """
    Filtra la respuesta para devolver tanto un mensaje para el usuario como el contenido del código.
    """
    # Detectar si hay bloques de código
    if re.search(r'```.*?```', response_text, flags=re.DOTALL) or re.search(r'`.*?`', response_text):
        # Extraer el código y devolver el mensaje y el código por separado
        code_block = re.findall(r'```.*?```', response_text, flags=re.DOTALL)
        code_block = "\n".join(code_block).replace('```', '')  # Eliminar las comillas invertidas

        return {
            "message": "Puedes descargar el código si gustas.",
            "code": code_block
        }

    # Sanitización normal si no es código
    response_text = re.sub(r'[^a-zA-Z0-9áéíóúñÁÉÍÓÚÑ\s.,?!]', '', response_text)

    return {
        "message": response_text,
        "code": ""
    }


def format_math_expression(text):
    # Convertir todas las letras a minúsculas
    formatted_text = text.lower()

    # Reemplazar los paréntesis incorrectos {} y [] por ()
    formatted_text = re.sub(r'[\{\}\[\]]', '(', formatted_text)

    # Insertar el operador de multiplicación entre un número y una variable si falta (ejemplo: 4x -> 4*x)
    formatted_text = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', formatted_text)

    # Insertar el operador de multiplicación entre un número y un paréntesis si falta
    formatted_text = re.sub(r'(\d)(\()', r'\1*\2', formatted_text)  # Ejemplo: 3(x) -> 3*(x)

    # Insertar el operador de multiplicación entre una variable y un paréntesis si falta
    formatted_text = re.sub(r'(\w)(\()', r'\1*\2', formatted_text)  # Ejemplo: x(x) -> x*(x)

    # Reemplazar cualquier carácter no permitido en las expresiones matemáticas
    formatted_text = re.sub(r'[^\d\w\s\(\)\=\+\-\*/\.]', '', formatted_text)

    # Asegurarse de que no haya dobles operadores, por ejemplo: ++, --
    formatted_text = re.sub(r'\+\+|\-\-', '', formatted_text)

    # Eliminar espacios adicionales
    formatted_text = formatted_text.replace(" ", "")

    return formatted_text

def is_valid_extracted_text(text):
    # Eliminar espacios en blanco y contar el número de letras
    cleaned_text = re.sub(r'\s+', '', text)
    if len(cleaned_text) < 5:  # Si hay menos de 5 caracteres, puede que no haya contenido válido
        return False
    return True
