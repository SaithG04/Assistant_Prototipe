import re


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
