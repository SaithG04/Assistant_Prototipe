import speech_recognition as spd
from pydub import AudioSegment
from io import BytesIO
from math_operations import solve_simple_math_operation
from general_commands import handle_general_query
from transformers import pipeline

listener = spd.Recognizer()

# Cargar el modelo preentrenado para clasificación de intenciones
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def classify_intent(text):
    """
    Clasifica la intención del texto usando un modelo preentrenado y un umbral de decisión.
    """
    labels = ["operación matemática", "consulta general"]
    result = classifier(text, labels)

    # Mostrar la clasificación completa para depuración
    print(f"Clasificación obtenida: {result}")

    # Ajustar umbral para clasificar
    threshold = 0.25
    top_label = result['labels'][0]
    top_score = result['scores'][0]

    if top_score >= threshold:
        return top_label
    else:
        return 'desconocido'  # Devuelve 'desconocido' si no hay una confianza suficiente


# Diccionario que asocia cada tipo de comando con una función
intent_dispatcher = {
    'operación matemática': solve_simple_math_operation,
    'consulta general': handle_general_query,
    'procesar imagen': 'abrir cámara',  # Señal para abrir cámara en frontend
    # Puedes seguir agregando comandos aquí
}


def detect_intent(text):
    """
    Detecta la intención (tipo de comando) basándose en las palabras clave en el texto.
    """
    # Detectar operaciones matemáticas manualmente
    if text.startswith("cuánto es") or text.startswith("cuanto es"):
        return 'operación matemática'

    # Si no es matemática, usar el clasificador de IA para otras intenciones
    intent = classify_intent(text)
    print(f"Intención detectada por IA: {intent}")

    if intent in intent_dispatcher:
        return intent
    return 'desconocido'


def dispatch_command(text):
    """
    Esta función decide qué tipo de comando es y llama a la función correspondiente.
    """
    print(f"Texto recibido para procesar comando: {text}")

    intent = detect_intent(text)
    print(f"Intención detectada: {intent}")

    # Buscar la intención en el diccionario
    #if intent == 'procesar imagen':
        # Devolver señal para abrir la cámara en el frontend
    #    return "abrir cámara"

    command_function = intent_dispatcher.get(intent)
    if command_function:
        return command_function(text)
    return "No pude entender el comando."


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
            print(f"Texto transcrito: {texto}")
            return texto
    except spd.UnknownValueError:
        return None
    except spd.RequestError as e:
        print(f"Error al realizar la solicitud a la API de Google: {e}")
        return None
