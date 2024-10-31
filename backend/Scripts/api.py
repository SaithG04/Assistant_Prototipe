import io
from flask import Flask, request, jsonify, send_file, make_response
from voice import convert_audio_to_wav, transcribe_audio, dispatch_command
import logging

# Configurar el logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Configuración de la base de datos
logging.debug("Inicializando conexión a la base de datos")


@app.route('/process_voice_command', methods=['POST'])
def process_voice_command():
    logging.debug("Recibiendo solicitud para procesar comando de voz")

    if 'file' not in request.files:
        logging.error("Archivo de audio no encontrado en la solicitud")
        return jsonify({'error': 'No se encontró un archivo de audio'}), 400

    audio_file = request.files['file']
    file_ext = audio_file.filename.split('.')[-1]
    logging.debug(f"Archivo recibido: {audio_file.filename}, extensión: {file_ext}")

    if audio_file.filename == '':
        logging.error("El archivo de audio está vacío")
        return jsonify({'error': 'El archivo de audio está vacío.'}), 400

    # Convertir el archivo a WAV si no está en ese formato
    audio_file = convert_audio_to_wav(audio_file, file_ext)
    logging.debug("Archivo convertido a formato WAV")

    # Llamar a la función que transcribe el audio a texto
    transcribed_text = transcribe_audio(audio_file)
    logging.debug(f"Texto transcrito: {transcribed_text}")

    if transcribed_text is None:
        logging.error("No se pudo transcribir el audio")
        return jsonify({'error': '¿Dijiste algo? No te escuché'}), 400

    try:
        # Procesar el texto transcrito y enviar a Gemini
        response_text = dispatch_command(transcribed_text)
        logging.debug(f"Texto procesado por Gemini: {response_text}")
        return jsonify({'texto': response_text, 'mensaje': 'Texto procesado correctamente.'})
    except Exception as e:
        logging.error(f"Error interno al procesar el comando de voz: {e}")
        return jsonify({'error': f'Ha ocurrido un error'}), 500


@app.route('/process_image_and_audio', methods=['POST'])
def process_image_and_audio():
    logging.debug("Recibiendo solicitud para procesar imagen y audio")

    if 'image' not in request.files or 'audio' not in request.files:
        logging.error("Imagen o archivo de audio no encontrados")
        return jsonify({'error': 'Imagen o archivo de audio no encontrados.'}), 400

    image_file = request.files['image']
    audio_file = request.files['audio']
    logging.debug(
        f"Archivo de imagen recibido: {image_file.filename}, Archivo de audio recibido: {audio_file.filename}")

    try:
        file_ext = audio_file.filename.split('.')[-1]
        if audio_file.filename == '':
            logging.error("El archivo de audio está vacío")
            return jsonify({'error': 'El archivo de audio está vacío.'}), 400

        # Convertir el archivo a WAV si no está en ese formato
        audio_file = convert_audio_to_wav(audio_file, file_ext)
        # Transcribir el audio
        transcribed_text = transcribe_audio(audio_file)
        logging.debug(f"Texto transcrito del audio: {transcribed_text}")

        # Pasar el comando y la imagen al método dispatch_command
        result = dispatch_command(transcribed_text, image_file)
        logging.debug(f"Resultado de dispatch_command: {result}")

        if isinstance(result, io.BytesIO):
            message = "Aquí tienes el resultado."
            response = make_response(send_file(result, mimetype='image/jpeg'))
            response.headers['message'] = message
            logging.debug("Enviando imagen convertida")
            return response
        else:
            return jsonify({'mensaje': result})

    except Exception as e:
        logging.error(f"Error al procesar imagen y audio: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logging.debug("Iniciando servidor Flask en el puerto 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
