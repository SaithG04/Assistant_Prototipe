import io
import json
import re
from datetime import datetime, timedelta

from PIL import Image
import speech_recognition as spd
from pydub import AudioSegment
from io import BytesIO
import logging

from process_image import classify_image, preprocess_image, convert_image_to_bytes, is_image_blank, \
    improve_image_resolution
from consult_taks import add_task, list_tasks
from consults_reniec import get_info_by_dni
from db import list_tasks_by_date_and_status, list_schedule_by_day
from generate_image import generate_solution_image
from prompts import generate_task_creation_prompt, generate_natural_date_time_prompt, \
    generate_task_list_natural_prompt, generate_task_date_interpretation_prompt, generate_schedule_list_natural_prompt, \
    generate_schedule_date_interpretation_prompt, generate_ethical_check_prompt
from recon_math import extract_text_from_image
from solve_math import solve_math_expression
from text_processing import preprocess_text, sanitize_response, format_math_expression, day_translation
from gemini_interaction import interact_with_gemini

# Configurar el logging
logging.basicConfig(level=logging.DEBUG)

listener = spd.Recognizer()


def convert_audio_to_wav(audio_file, file_ext):
    """
    Convierte el archivo de audio a formato WAV si no está en ese formato.
    """
    logging.debug(f"Convirtiendo el archivo de audio de formato {file_ext} a WAV.")
    if file_ext != 'wav':
        audio_segment = AudioSegment.from_file(BytesIO(audio_file.read()), format=file_ext)
        audio_file = BytesIO()
        audio_segment.export(audio_file, format='wav')
        audio_file.seek(0)  # Reinicia el puntero del archivo
    return audio_file


def transcribe_audio(audio_file):
    """
    Transcribe el audio proporcionado a texto usando Google Speech Recognition.
    """
    logging.debug("Iniciando la transcripción del archivo de audio.")
    try:
        with spd.AudioFile(audio_file) as src:
            audio_data = listener.record(src)  # Lee el audio completo
            texto = listener.recognize_google(audio_data, language="es-ES")  # Realiza la transcripción
            texto = texto.lower()  # Convierte el texto a minúsculas
            logging.debug(f"Texto transcrito: {texto}")
            return texto
    except spd.UnknownValueError:
        logging.error("No se pudo entender el audio.")
        return None
    except spd.RequestError as e:
        logging.error(f"Error al realizar la solicitud a la API de Google: {e}")
        return None


def dispatch_command(text, image_file=None):
    """
    Procesa el texto transcrito con Gemini si no es un comando específico.
    Si se incluye una imagen, también se procesa de acuerdo con el comando.
    """
    logging.debug(f"Comando recibido: {text}")

    # Verificar si el texto comienza con "consultar horario"
    if text.startswith("consultar horario"):
        logging.debug("Comando de consulta de horario identificado.")

        # Obtener la fecha actual para enviar como contexto a Gemini
        today_date = datetime.now()
        logging.debug(f"Fecha actual: {today_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # Si el usuario dice solo "consultar horario", usamos el día de hoy
        if text.strip() == "consultar horario":
            day_of_week = today_date.strftime('%A')  # Ejemplo: "Wednesday"
            logging.debug(f"Día de la semana obtenido directamente de la fecha actual: {day_of_week}")
        else:
            # Generar el prompt para interpretar la fecha
            date_interpretation_prompt = generate_schedule_date_interpretation_prompt(text, today_date)
            logging.debug(f"Enviando a Gemini para interpretar la fecha: {date_interpretation_prompt}")

            # Usar la IA para interpretar la fecha
            response_from_gemini = interact_with_gemini(date_interpretation_prompt, False)
            logging.debug(f"Respuesta de Gemini para la fecha interpretada: {response_from_gemini}")

            # Parsear la respuesta de Gemini para obtener la fecha
            try:
                cleaned_response = re.sub(r'```json|```', '', response_from_gemini).strip()
                logging.debug(f"Respuesta limpiada de Gemini: {cleaned_response}")

                date_data = json.loads(cleaned_response)
                query_date = datetime.strptime(date_data['date'], '%Y-%m-%d')
                day_of_week = query_date.strftime('%A')  # Obtener el día de la semana en inglés
                logging.debug(f"Día de la semana obtenido de la fecha interpretada: {day_of_week}")
            except json.JSONDecodeError as e:
                logging.error(f"Error al interpretar la respuesta de Gemini: {str(e)}")
                return "Hubo un error al procesar la fecha del horario."

        # Traducir el día de la semana de inglés a español usando el diccionario
        day_of_week_es = day_translation.get(day_of_week,
                                             day_of_week)  # Por si acaso Gemini devuelve un valor inesperado
        logging.debug(f"Día de la semana traducido a español: {day_of_week_es}")

        # Consultar el horario para el día de la semana interpretado y traducido
        schedule_items = list_schedule_by_day(day_of_week_es)
        logging.debug(f"Items de horario encontrados para {day_of_week_es}: {schedule_items}")

        # Verificar si hay clases para el día consultado
        if not schedule_items:
            logging.info(f"No se encontraron clases para el {day_of_week_es}.")
            return f"No tienes clases programadas para el {day_of_week_es}."

        # Generar el prompt y obtener respuesta natural de Gemini
        schedule_list_prompt = generate_schedule_list_natural_prompt(schedule_items)
        logging.debug(f"Enviando a Gemini para transformar la lista de horarios: {schedule_list_prompt}")

        response_from_gemini = interact_with_gemini(schedule_list_prompt, False)
        logging.debug(f"Respuesta de Gemini con el horario en formato natural: {response_from_gemini}")

        return f"Clases para {day_of_week_es}:\n{response_from_gemini}"

    # Verificar si el texto comienza con "consultar dni" seguido de un DNI de 8 dígitos
    elif text.startswith("consultar dni"):
        logging.debug("Comando de consulta de DNI identificado.")
        match = re.search(r'\b\d{8}\b', text)
        if match:
            dni = match.group(0)
            logging.debug(f"DNI extraído: {dni}")
            info = get_info_by_dni(dni)
            if info:
                logging.debug(f"Información del DNI: {info}")
                return info
            else:
                logging.info("No se encontró información para el DNI proporcionado.")
                return "No se encontró información para el DNI proporcionado."
        else:
            logging.warning("DNI no válido proporcionado.")
            return "DNI inválido. Asegúrate de proporcionar un DNI de 8 dígitos."

    # Procesar el comando de convertir imagen
    elif text.startswith("procesar imagen"):
        logging.debug("Comando de procesamiento de imagen identificado.")

        # Verificar si se proporciona una imagen
        if not image_file:
            logging.warning("No se proporcionó una imagen para procesar.")
            return "No se ha proporcionado una imagen para procesar."

        # Determinar el tipo de procesamiento solicitado
        if "blanco y negro" in text or "blanco y negro" in text:
            logging.debug("Procesamiento: conversión a blanco y negro.")
            try:
                image = Image.open(image_file).convert('L')  # Convertir a blanco y negro
                img_io = io.BytesIO()
                image.save(img_io, 'JPEG')
                img_io.seek(0)
                logging.debug("Imagen convertida a blanco y negro.")
                return img_io  # Devolver imagen procesada
            except Exception as e:
                logging.error(f"Error al procesar la imagen a blanco y negro: {str(e)}")
                return f"Error al procesar la imagen: {str(e)}"

        elif "mejorar calidad" in text or "super resolución" in text:
            logging.debug("Procesamiento: mejora de calidad de imagen.")
            try:
                high_res_image = improve_image_resolution(image_file)
                logging.debug("Imagen mejorada en resolución.")
                return high_res_image  # Devolver imagen mejorada
            except Exception as e:
                logging.error(f"Error al mejorar la calidad de la imagen: {str(e)}")
                return f"Error al mejorar la calidad de la imagen: {str(e)}"

        # Si no se especifica la acción, informar al usuario de las opciones disponibles
        else:
            logging.info("No se especificó el tipo de procesamiento para la imagen.")
            return "Por favor, indica si deseas 'convertir a blanco y negro' o 'mejorar calidad'."

    elif text.startswith("resolver operación matemática"):
        logging.debug("Comando de resolver ecuación detectado.")

        # Clasificar la imagen para verificar si contiene matemáticas
        classification = classify_image(image_file)
        logging.debug(f"Clasificación de la imagen: {classification}")

        # if "mathematics" in classification:
        if True:

            # Preprocesar la imagen
            image = preprocess_image(image_file)

            # Convertir la imagen preprocesada a flujo de bytes
            image_file = convert_image_to_bytes(image)

            # Verificar si la imagen está básicamente en blanco
            if is_image_blank(image_file):
                logging.warning("La imagen parece estar vacía o en blanco.")
                return "La imagen está vacía o no contiene texto útil."

            # Extraer texto de la imagen
            extracted_text = extract_text_from_image(image_file)
            logging.debug(f"Texto extraído de la imagen: {extracted_text}")

            # Limpiar el texto extraído
            cleaned_text = format_math_expression(extracted_text)
            logging.debug(f"Texto limpiado: {cleaned_text}")

            # Verificar si el texto contiene una ecuación válida antes de intentar resolverla
            if re.search(r'=', cleaned_text):  # Verificar que tenga un '=' para ser una ecuación
                # Resolver la ecuación
                solution = solve_math_expression(cleaned_text)
                logging.debug(f"Solución de la ecuación: {solution}")

                # Generar la imagen con la ecuación y la solución
                image_result = generate_solution_image(cleaned_text, solution)
                logging.debug("Imagen con la solución generada exitosamente.")
                return image_result
            else:
                logging.warning("El texto extraído no parece contener una ecuación matemática.")
                return "El texto extraído no parece contener una ecuación matemática."
        # else:
        #    return "La imagen no parece contener un ejercicio matemático."

    elif text.startswith("consultar tareas"):

        logging.debug("Comando de consulta de tareas identificado.")
        # Obtener la fecha actual para enviarla como contexto a Gemini, en caso de necesitar interpretación de fecha
        today_date = datetime.now()
        # Verificar si el usuario quiere consultar todas las tareas pendientes sin especificar una fecha
        if text.strip().lower() == "consultar tareas":
            logging.debug("Consultando todas las tareas pendientes.")
            # Consulta directa de todas las tareas pendientes
            tasks = list_tasks_by_date_and_status(status="pendiente")
            if not tasks:
                return "No tienes tareas pendientes."

            # Crear el prompt para obtener la lista en un formato natural
            task_list_prompt = generate_task_list_natural_prompt(tasks)
            response_from_gemini = interact_with_gemini(task_list_prompt, False)
            return f"Tareas pendientes:\n{response_from_gemini}"
        else:

            # Generar el prompt para que Gemini interprete la fecha en caso de haber especificado una
            date_interpretation_prompt = generate_task_date_interpretation_prompt(text, today_date)
            logging.debug(f"Enviando a Gemini para interpretar la fecha: {date_interpretation_prompt}")

            # Usar la IA para interpretar la fecha
            response_from_gemini = interact_with_gemini(date_interpretation_prompt, False)
            logging.debug(f"Respuesta de Gemini para la fecha interpretada: {response_from_gemini}")

            # Parsear la respuesta de Gemini
            try:

                cleaned_response = re.sub(r'```json|```', '', response_from_gemini).strip()
                date_data = json.loads(cleaned_response)

                # Si se ha interpretado una fecha válida, realizar la consulta
                if 'date' in date_data and date_data['date'] is not None:

                    query_date = datetime.strptime(date_data['date'], '%Y-%m-%d')
                    tasks = list_tasks_by_date_and_status(query_date, status="pendiente")

                    if not tasks:
                        return f"No tienes tareas pendientes para el {query_date.strftime('%d de %B')}."

                    # Crear el prompt para obtener la lista de tareas en un formato natural
                    task_list_prompt = generate_task_list_natural_prompt(tasks)
                    response_from_gemini = interact_with_gemini(task_list_prompt, False)

                    return f"Tareas pendientes para el {query_date.strftime('%d de %B')}:\n{response_from_gemini}"
                else:
                    return "No se especificó una fecha clara, y no se encontraron tareas pendientes específicas."
            except json.JSONDecodeError as e:

                logging.error(f"Error al interpretar la respuesta de Gemini: {str(e)}")
                return "Hubo un error al procesar los datos de la tarea."

    # Comando para crear una tarea
    elif text.startswith("crear tarea"):
        logging.debug("Comando de creación de tarea identificado.")

        # Obtener la fecha y hora actuales
        current_date_time = datetime.now()

        # Generar el prompt específico para la creación de tarea
        task_creation_prompt = generate_task_creation_prompt(text, current_date_time)
        logging.debug(f"Enviando a Gemini: {task_creation_prompt}")

        # Usar la IA para transformar la instrucción en formato JSON
        response_from_gemini = interact_with_gemini(task_creation_prompt, False)
        logging.debug(f"Respuesta de Gemini: {response_from_gemini}")

        try:
            # Limpiar el formato de Markdown y comillas triples
            cleaned_response = re.sub(r'```json|```', '', response_from_gemini).strip()
            logging.debug(f"Respuesta limpiada: {cleaned_response}")

            # Intentar analizar la respuesta como JSON
            task_data = json.loads(cleaned_response)
            logging.debug(f"Datos de tarea procesados: {task_data}")

            # Verificar que todos los campos necesarios estén presentes
            if 'name' in task_data and 'due_date' in task_data:
                name = task_data['name']
                description = task_data.get('description', 'Sin descripción')
                due_date_str = task_data['due_date']

                # Convertir la fecha y la hora en un objeto datetime
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S')
                logging.debug(f"Fecha y hora de vencimiento: {due_date}")

                # Crear la tarea usando la lógica de consult_tasks.py, con estado "pendiente"
                if add_task(name, description, due_date, status="pendiente"):
                    # Después de crear la tarea, generar una respuesta en lenguaje natural
                    natural_date_time_prompt = generate_natural_date_time_prompt(due_date)
                    formatted_due_date = interact_with_gemini(natural_date_time_prompt, False)
                    formatted_due_date = formatted_due_date.lower()
                    logging.debug(f"Fecha natural generada: {formatted_due_date}")

                    return f"Tarea '{name}' creada exitosamente para {formatted_due_date}."
                else:
                    return "Hubo un error al crear la tarea."

            else:
                logging.error("Faltan datos en la respuesta de Gemini.")
                return "No se pudieron encontrar todos los datos necesarios para la tarea."

        except json.JSONDecodeError as jde:
            logging.error(f"Error al procesar la respuesta de Gemini: {jde}")
            return "Hubo un error al procesar los datos de la tarea."
        except ValueError as ve:
            logging.error(f"Error al procesar la fecha y hora de la tarea: {ve}")
            return "Hubo un error con la fecha y hora de la tarea."

    # Dentro del bloque principal para "consultar a gemini"
    elif text.startswith("consultar a gemini") or text.startswith("consultar a géminis"):

        logging.debug("El usuario ha solicitado una consulta a Gemini.")
        # Generar el prompt de revisión ética
        ethical_check_prompt = generate_ethical_check_prompt(text)
        logging.debug(f"Enviando a Gemini para revisión ética: {ethical_check_prompt}")

        # Revisar la consulta en Gemini
        ethical_response = interact_with_gemini(ethical_check_prompt, False)
        logging.debug(f"Respuesta de Gemini para la revisión ética: {ethical_response}")

        # Evaluar la respuesta de Gemini para el control ético
        if "inapropiado" in ethical_response.lower():
            logging.warning("Consulta inapropiada detectada por revisión ética.")
            return ethical_response
            # return "La consulta contiene contenido inapropiado y no puede ser procesada."

        # Si es adecuado, enviar la consulta original a Gemini
        logging.debug("Consulta adecuada, procediendo con la solicitud en Gemini.")
        preprocessed_text = preprocess_text(text)
        response = interact_with_gemini(preprocessed_text, True)
        sanitized_response = sanitize_response(response)
        logging.debug(f"Respuesta de Gemini: {sanitized_response}")

        return sanitized_response

    elif text.startswith("consultar información académica"):
        logging.debug("Comando de consulta de información académica identificado.")

        # Mensaje descriptivo sobre la Universidad César Vallejo
        academic_info = (
            "La Universidad César Vallejo (UCV) es una institución privada fundada en 1991 en Trujillo, Perú. "
            "Su misión es brindar una educación de calidad, con un enfoque en la investigación, la innovación y la responsabilidad social. "
            "La UCV ofrece una amplia variedad de programas académicos en diversas áreas como ingeniería, ciencias de la salud, negocios, derecho, entre otros. "
            "Cuenta con sedes en diferentes ciudades del país, incluyendo Lima, Piura, Chiclayo, y Arequipa, lo que facilita el acceso a la educación superior en diversas regiones. "
            "Para los estudiantes, la UCV proporciona recursos académicos, bibliotecas, y acceso a plataformas digitales que permiten una formación integral y adaptable a los tiempos actuales. "
            "Además, la universidad fomenta el desarrollo profesional a través de convenios con empresas y programas de prácticas pre-profesionales. "
            "La UCV se caracteriza por su compromiso en formar profesionales competentes, éticos y con una visión global."
        )

        logging.debug(f"Información académica proporcionada: {academic_info}")
        return academic_info

    elif text.strip().lower() == "listar comandos":

        logging.debug("Listando comandos...")
        # Definir los comandos y sus descripciones en un formato amigable para voz
        commands = {

            "Consultar horario": "Te digo el horario de clases para hoy o para una fecha que menciones.",
            "Consultar tareas": "Te muestro todas las tareas pendientes o las tareas de una fecha específica.",
            "Crear tarea": "Crea una nueva tarea con el nombre, descripción, fecha y hora que indiques.",
            "Procesar imagen a blanco y negro": "Convierte una imagen a blanco y negro y la procesa.",
            "Resolver operación matemática": "Resuelve una operación algebráica en una imagen.",
            "Consultar DNI": "Consulta información de una persona usando su número de DNI.",
            "Consultar a gemini": "Puedes hacerle una pregunta abierta para obtener una respuesta de la inteligencia "
                                  "artificial Gémini."
        }

        # Formatear la lista de comandos para que sea fácil de escuchar y visualizar
        command_list = "\n".join([f"{command}: {description}" for command, description in commands.items()])
        response = f"Tengo varios comandos disponibles:\n\n{command_list}\n\nPuedes pedirme cualquiera de estos."

        logging.debug("Lista de comandos generada en formato de voz y visual.")
        return response

    else:
        return 'No te entendí, di "listar comandos" para mostrarte los comandos disponibles'
