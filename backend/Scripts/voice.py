import re

import speech_recognition as spd
from pydub import AudioSegment
from io import BytesIO

from Scripts.consults_reniec import get_info_by_dni
from text_processing import preprocess_text, sanitize_response
from gemini_interaction import interact_with_gemini

listener = spd.Recognizer()


def convert_audio_to_wav(audio_file, file_ext):
    """
    Convierte el archivo de audio a formato WAV si no está en ese formato.
    """
    if file_ext != 'wav':
        print("Convirtiendo el archivo a formato WAV...")
        audio_segment = AudioSegment.from_file(BytesIO(audio_file.read()), format=file_ext)
        audio_file = BytesIO()
        audio_segment.export(audio_file, format='wav')
        audio_file.seek(0)  # Reinicia el puntero del archivo
    return audio_file


def transcribe_audio(audio_file):
    """
    Transcribe el audio proporcionado a texto usando Google Speech Recognition.
    """
    try:
        with spd.AudioFile(audio_file) as src:
            audio_data = listener.record(src)  # Lee el audio completo
            texto = listener.recognize_google(audio_data, language="es-ES")  # Realiza la transcripción
            texto = texto.lower()  # Convierte el texto a minúsculas
            print(f"Texto transcrito: {texto}")  # Imprime el texto transcrito
            return texto
    except spd.UnknownValueError:
        print("No se pudo entender el audio.")
        return None
    except spd.RequestError as e:
        print(f"Error al realizar la solicitud a la API de Google: {e}")
        return None


def dispatch_command(text):
    """
    Procesa el texto transcrito con Gemini si no es un comando específico enviado desde el frontend.
    """
    # Verificar si el texto comienza con "consultar horario"
    if text.startswith("consultar horario"):
        # Aquí puedes procesar el comando de consulta de horario
        return "Comando para consultar horario identificado."

    # Verificar si el texto comienza con "consultar dni" seguido de un DNI de 8 dígitos
    elif text.startswith("consultar dni"):
        # Extraer el DNI de 8 dígitos usando tu función
        match = re.search(r'\b\d{8}\b', text)
        if match:
            dni = match.group(0)  # Extraer el DNI
            # Llamar a la función para obtener información por DNI
            info = get_info_by_dni(dni)
            if info:
                return info
            else:
                return "No se encontró información para el DNI proporcionado."
        else:
            return "DNI inválido. Asegúrate de proporcionar un DNI de 8 dígitos."

    elif text.startswith("consultar tareas"):
        # Aquí puedes procesar el comando para consultar tareas
        return "Comando para consultar tareas identificado."

    elif text.startswith("consultar"):
        return "Comando no identificado."

    # Si no es ningún comando específico, procesar normalmente con Gemini
    preprocessed_text = preprocess_text(text)
    response = interact_with_gemini(preprocessed_text)
    sanitized_response = sanitize_response(response)

    return sanitized_response

