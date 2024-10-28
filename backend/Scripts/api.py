from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Scripts.consults_reniec import get_info_by_dni
from Scripts.voice import convert_audio_to_wav, transcribe_audio, dispatch_command
from db import Task, get_schedule_by_day
from config import DATABASE_URL

app = Flask(__name__)

# Configuración de la base de datos
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/process_voice_command', methods=['POST'])
def process_voice_command():  # Cambié el nombre de la función
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró un archivo de audio'}), 400

    audio_file = request.files['file']
    file_ext = audio_file.filename.split('.')[-1]

    if audio_file.filename == '':
        return jsonify({'error': 'El archivo de audio está vacío.'}), 400

    # Convertir el archivo a WAV si no está en ese formato
    audio_file = convert_audio_to_wav(audio_file, file_ext)

    # Llamar a la función que transcribe el audio a texto
    transcribed_text = transcribe_audio(audio_file)

    if transcribed_text is None:
        return jsonify({'error': 'No se pudo transcribir el audio'}), 400

    try:
        # Procesar el texto transcrito y enviar a Gemini
        response_text = dispatch_command(transcribed_text)
        return jsonify({'texto': response_text, 'mensaje': 'Texto procesado correctamente.'})
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@app.route('/get_schedule/<day_of_week>', methods=['GET'])
def get_schedule_route(day_of_week):
    try:
        schedule = get_schedule_by_day(day_of_week.capitalize())
        if not schedule:
            return jsonify({'mensaje': f'No tienes clases programadas para el {day_of_week}.'}), 200

        result = [
            {
                'subject': entry.subject,
                'start_time': entry.start_time.strftime('%H:%M'),
                'end_time': entry.end_time.strftime('%H:%M'),
                'location': entry.location
            } for entry in schedule
        ]
        return jsonify({'horario': result, 'mensaje': f'Horario para el {day_of_week} consultado exitosamente.'}), 200

    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@app.route('/get_dni/<dni>', methods=['GET'])
def get_dni(dni):
    try:
        # Usar la función get_info_by_dni del archivo consults_reniec.py
        result = get_info_by_dni(dni)
        if not result:
            return jsonify({'mensaje': 'No se encontró información para el DNI proporcionado.'}), 404

        # Retornar la información obtenida
        return jsonify({'dni_info': result, 'mensaje': 'Consulta de DNI exitosa.'}), 200

    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = session.query(Task).all()  # Asegúrate de que Task esté bien definido en tu modelo
        if not tasks:
            return jsonify({'mensaje': 'No tienes tareas pendientes.'}), 200

        result = [
            {
                'task_name': task.name,
                'due_date': task.due_date.strftime('%d/%m/%Y'),
                'description': task.description
            } for task in tasks
        ]
        return jsonify({'tareas': result, 'mensaje': 'Tareas consultadas exitosamente.'}), 200

    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
