def generate_task_creation_prompt(text, current_date_time):
    """
    Genera un prompt claro para la creación de tareas basado en la instrucción del usuario,
    incluyendo la columna `status` por defecto como "pendiente".
    """
    current_date = current_date_time.strftime('%Y-%m-%d')
    current_time = current_date_time.strftime('%H:%M:%S')

    prompt = f"""
    El usuario ha dado la siguiente instrucción para crear una tarea: '{text}'.

    Extrae y devuelve los siguientes campos en JSON:
    - **name**: El nombre de la tarea.
    - **description**: Breve descripción. Si no se menciona, usa "Sin descripción".
    - **due_date**: La fecha de vencimiento en formato "YYYY-MM-DD HH:MM:SS":
      - Si la fecha no se menciona, asigna mañana a la misma hora '{current_time}' de hoy '{current_date}'.
      - Si solo se menciona la fecha (sin hora), asigna "00:00:00" para ese día.
      - Si solo se menciona la hora (sin fecha), asume hoy '{current_date}' o mañana si la hora ya pasó.
    - **status**: Coloca siempre "pendiente" para indicar que la tarea está activa.

    Devuelve **siempre** en JSON estructurado, por ejemplo:

    ```json
    {{
      "name": "comprar comida",
      "description": "Sin descripción",
      "due_date": "2023-03-08 11:00:00",
      "status": "pendiente"
    }}
    ```

    Asegúrate de que el JSON esté completo y correcto, sin valores nulos.
    """
    return prompt


def generate_natural_date_time_prompt(due_date):
    """
    Genera un prompt claro para transformar una fecha y hora en formato natural, por ejemplo:
    "cuatro de la tarde de mañana ocho de marzo"
    """
    prompt = f"""
    Transforma la siguiente fecha y hora en un formato natural en español: '{due_date.strftime('%Y-%m-%d %H:%M:%S')}'.

    Reglas:
    - Usa "hoy" o "mañana" cuando corresponda. Si la fecha es dentro de los próximos dos días, usa esos términos.
    - Si la fecha es después de mañana, escribe el día y el mes completos, usando nombres de los meses y días.
    - La hora debe expresarse en formato de 12 horas, usando "de la mañana", "de la tarde" o "de la noche" según corresponda.
    - Asegúrate de que las horas de la tarde (después de las 12:00 y antes de las 18:00) se expresen correctamente.
    - Para horas exactas (en punto), no incluyas los minutos. Para cualquier otra hora, incluye los minutos.
    - Usa palabras en lugar de números para las horas y fechas. Por ejemplo: "una de la tarde" en lugar de "13:00", y "ocho de marzo" en lugar de "08/03".
    - Si es antes de las doce, usa "de la mañana"; después de las doce, usa "de la tarde" o "de la noche" según corresponda.
    - Asegúrate de no incluir números en la respuesta, todos deben estar escritos en palabras.

    Devuelve la fecha y hora en un formato claro y natural, como: "una y treinta y siete de la tarde del jueves treinta y uno de octubre".
    """
    return prompt


def generate_task_list_natural_prompt(tasks):
    task_details = "\n".join([
        f"Tarea: {task.name}, Descripción: {task.description}, Fecha y Hora: {task.due_date.strftime('%Y-%m-%d %H:%M:%S')}, Estado: {task.status}"
        for task in tasks
    ])

    prompt = f"""
    Aquí tienes la lista de tareas:

    {task_details}

    Por favor, transforma esta lista en un formato natural en español. Reglas:
    - Usa palabras en lugar de números para las horas y fechas.
    - Incluye el estado de cada tarea en formato coloquial: "pendiente", "completada" o "cancelada".
    - La fecha y hora deben estar en un formato claro como "dos de la tarde del ocho de marzo".
    - Mantén cada tarea en una línea separada.

    Devuelve la lista de tareas en un formato natural y claro.
    """
    return prompt


def generate_task_date_interpretation_prompt(text, current_date):
    """
    Genera un prompt para que Gemini interprete la fecha mencionada en la instrucción del usuario y devuelva solo la fecha interpretada.
    """
    # Convertir la fecha actual a un formato de referencia
    current_date_str = current_date.strftime('%Y-%m-%d')

    prompt = f"""
    El usuario ha solicitado: '{text}'.
    Interpreta la fecha a partir de la instrucción y devuélvela en formato JSON. Usa '{current_date_str}' como la fecha actual de referencia.

    Considera lo siguiente:
    - Si el usuario dice "hoy", "mañana" o "pasado mañana", devuelve la fecha correspondiente en el formato "YYYY-MM-DD" basado en la fecha de referencia '{current_date_str}'.
    - Si el usuario menciona una fecha específica en palabras, como "dos de noviembre", convierte esa fecha al formato "YYYY-MM-DD".
    - Si no se menciona una fecha específica en la instrucción, devuelve `"date": null` en el JSON para indicar que no se ha especificado una fecha.

    Devuelve solo la fecha interpretada en JSON puro, sin texto adicional ni comentarios:

    ```json
    {{
      "date": "YYYY-MM-DD" o null
    }}
    ```

    Asegúrate de no incluir texto adicional ni comentarios fuera del formato JSON especificado.
    """
    return prompt


def generate_schedule_date_interpretation_prompt(text, current_date):
    """
    Genera un prompt para que Gemini interprete la fecha mencionada en la instrucción del usuario.
    """
    current_date_str = current_date.strftime('%Y-%m-%d')
    prompt = f"""
    El usuario ha solicitado: '{text}'.
    Interpreta la fecha a partir de la instrucción y devuélvela en formato JSON. Usa '{current_date_str}' como la fecha actual de referencia.
    Interpreta la fecha a partir de la instrucción, considerando lo siguiente:
    - Si el usuario dice "hoy", "mañana" o "pasado mañana", devuelve la fecha correspondiente en el formato "YYYY-MM-DD".
    - Si el usuario menciona una fecha específica en palabras, como "dos de noviembre", convierte esa fecha al formato "YYYY-MM-DD".
    - Si no se menciona una fecha, asume que el usuario quiere consultar el horario de hoy '{current_date.strftime('%Y-%m-%d')}'.

    Devuelve únicamente la fecha interpretada en un formato JSON claro:

    ```json
    {{
      "date": "YYYY-MM-DD"
    }}
    ```
    Asegúrate de no incluir texto adicional ni comentarios fuera del formato JSON especificado.
    """
    return prompt


def generate_schedule_list_natural_prompt(schedule_items):
    """
    Genera un prompt para que Gemini transforme la lista de clases en un formato natural sin
    asteriscos ni formato marcado, ideal para lectura en voz alta.
    """
    schedule_details = "\n".join([
        f"Clase de {item.subject} ({item.modality.lower()}) impartida por {item.professor}. "
        f"Empieza a las {item.start_time.strftime('%I:%M %p').lower()} y termina a las {item.end_time.strftime('%I:%M %p').lower()} "
        f"en {'el ' + item.location if item.modality == 'Presencial' else 'modalidad virtual'}."
        for item in schedule_items
    ])

    prompt = f"""
    Aquí tienes la lista de clases para el día solicitado:

    {schedule_details}

    Transforma esta lista en un formato natural en español, sin usar ningún tipo de formato marcado, como asteriscos, puntos, viñetas o cualquier símbolo especial. 
    Escribe cada clase como una oración completa. Si detectas clases que son del mismo tema, con el mismo docente, en el mismo lugar, pero se diferencian en que una es práctica y otra es teórica, combina esas descripciones en una sola oración, especificando que el mismo docente imparte ambas modalidades. 

    Asegúrate de que la respuesta sea clara y fácil de leer en voz alta, sin incluir elementos innecesarios. 

    Por ejemplo: "La clase de Patrones de Diseño de Realidad Virtual es presencial y será impartida por García Vargas, Henry Miller. 
    La teoría será de cinco y media a ocho de la noche y la práctica de ocho y diez a nueve y cincuenta de la noche en el Laboratorio de Computo F01101411."
    """
    return prompt


def generate_ethical_check_prompt(text):
    """
    Genera un prompt para que Gemini evalúe si la consulta es apropiada.
    """
    prompt = f"""
    Evalúa si el siguiente texto contiene contenido inapropiado, ofensivo o contrario a los principios éticos:

    "{text}"

    Si el texto es adecuado, responde solo con "aprobado". Si es inapropiado, responde con "inapropiado" y una breve razón del rechazo.
    """
    return prompt