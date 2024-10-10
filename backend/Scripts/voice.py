import speech_recognition as spd
import pyttsx3

# Inicializar el motor de síntesis de voz y el reconocimiento
listener = spd.Recognizer()
engine = pyttsx3.init()

# Configuración de la voz
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 180)  # Velocidad de habla


def speak(texto):
    """
    Función para convertir texto en habla.
    """
    engine.say(texto)
    engine.runAndWait()


def listen(audio_file=None):
    """
    Función para escuchar audio desde un archivo o desde el micrófono.
    Si se proporciona un archivo de audio, lo procesa, de lo contrario utiliza el micrófono.
    """
    entrada = ""
    try:
        if audio_file:
            # Procesar el archivo de audio
            with spd.AudioFile(audio_file) as src:
                audio = listener.record(src)  # Leer el archivo completo
            entrada = listener.recognize_google(audio, language="es-ES")  # Convertir el audio en texto
            entrada = entrada.lower()
        else:
            # Si no se proporciona archivo, usar el micrófono
            with spd.Microphone() as src:
                listener.adjust_for_ambient_noise(src)  # Ajustar para el ruido ambiental
                print("¡Habla ahora!")
                audio = listener.listen(src, timeout=5, phrase_time_limit=10)  # Escuchar la entrada de audio
                entrada = listener.recognize_google(audio, language="es-ES")
                entrada = entrada.lower()
    except spd.UnknownValueError:
        entrada = "Lo siento, no entendí eso."
    except spd.RequestError:
        entrada = "Fallo la solicitud; revisa tu conexión a internet."
    except Exception as e:
        entrada = f"Ocurrió un error: {e}"

    return entrada