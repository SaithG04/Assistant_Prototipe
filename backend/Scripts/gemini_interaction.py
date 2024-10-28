import google.generativeai as genai

from Scripts.db import save_message_to_db
from config import API_KEY
from difflib import SequenceMatcher  # Para detectar similitud en entradas

# Configurar la API de Gemini
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-pro")


# Función para medir la similitud de textos
def is_similar(text1, text2, threshold=0.8):
    """
    Compara dos textos y devuelve True si son similares en al menos un 'threshold' de similitud.
    """
    return SequenceMatcher(None, text1, text2).ratio() > threshold


def interact_with_gemini(text):
    """
    Envía el texto a Gemini AI junto con el historial de la conversación para mantener ex   l contexto.
    """
    try:
        print("Entrada del metodo interact.. " + text)
        # Cargar el historial desde la base de datos
        # print("Cargando historial de la base de datos...")
        # conversation_history = load_history_from_db()

        # Limitar el historial para que Gemini tenga contexto, pero no sea demasiado largo
        # conversation_history = conversation_history[-5:]

        # Convertir el historial de la base de datos en el formato requerido por Gemini
        history = []
        # for entry in conversation_history:
        #    if entry.role == 'assistant':
        #        gemini_role = 'model'
        #    else:
        #        gemini_role = entry.role
        #    history.append({"role": gemini_role, "parts": [{"text": entry.content}]})

        # Verificar si el usuario dijo algo muy similar antes
        # if conversation_history and conversation_history[-1].role == 'user'
        # and is_similar(conversation_history[-1].content, text):
        #    print("Entrada similar detectada. El usuario ya dijo algo muy parecido anteriormente.")
        #    return "Ya me has dicho algo muy similar antes, por favor di algo diferente."

        # Agregar el nuevo input del usuario al historial
        # history.append({"role": "user", "parts": [{"text": text}]})

        # print(f"Historial actualizado con el texto del usuario: {text}")

        # Iniciar la conversación con el historial y el nuevo mensaje
        chat = model.start_chat(history=history)

        # Enviar la nueva consulta a Gemini
        response = chat.send_message(text)
        print(f"Respuesta de Gemini recibida: {response.text}")

        # Verificar si la respuesta es muy similar a la última respuesta del asistente
        # if conversation_history and conversation_history[-1].role == 'assistant'
        #  and is_similar(conversation_history[-1].content, response.text):
        #    print("Respuesta similar detectada. No se enviará la misma respuesta.")
        #    return "Parece que te respondí algo similar antes, ¿puedes aclarar lo que dijiste?"

        # Guardar el mensaje del usuario y la respuesta de Gemini en la base de datos
        save_message_to_db("user", text)
        save_message_to_db("assistant", response.text)

        print("Mensaje guardado en la base de datos.")
        return response.text

    except Exception as e:
        print(f"Error en interact_with_gemini: {str(e)}")
        return "Hubo un error al procesar tu solicitud."
