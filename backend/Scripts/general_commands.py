def handle_general_query(text):
    """
    Maneja preguntas generales como "quién es" o "qué es".
    Esto es solo un ejemplo básico; podrías integrarlo con una API para obtener respuestas más sofisticadas.
    """
    if 'quién es' in text:
        return "Lo siento, no tengo información disponible sobre esa persona."
    elif 'qué es' in text:
        return "Eso es algo muy interesante, pero necesitaría más información para poder responder."

    return "No estoy seguro de cómo responder a eso."
